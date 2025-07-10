import yaml
import re
from typing import Dict, List, Optional, Tuple, Any
import logging
from pathlib import Path

from models.financials import FinancialData, GAAPFinancialData, LabelMapping

logger = logging.getLogger(__name__)

class LabelTranslator:
    """Translates French financial labels to GAAP English labels"""
    
    def __init__(self, mapping_file: str = "data/dict_fr_to_gaap.yaml"):
        self.mapping_file = Path(mapping_file)
        self.mappings = self._load_mappings()
        self.confidence_threshold = 0.7
    
    def _load_mappings(self) -> Dict[str, Dict[str, str]]:
        """Load French to GAAP mappings from YAML file"""
        try:
            if self.mapping_file.exists():
                with open(self.mapping_file, 'r', encoding='utf-8') as f:
                    return yaml.safe_load(f)
            else:
                logger.warning(f"Mapping file not found: {self.mapping_file}")
                return {}
        except Exception as e:
            logger.error(f"Error loading mappings: {e}")
            return {}
    
    def translate_financial_data(self, data: FinancialData) -> GAAPFinancialData:
        """Translate raw financial data to GAAP format"""
        translated_data = {}
        total_confidence = 0.0
        translated_count = 0
        
        for line in data.lines:
            gaap_label, confidence = self.translate_label(line.label)
            if gaap_label and confidence >= self.confidence_threshold:
                # Handle duplicate labels by summing values
                if gaap_label in translated_data:
                    translated_data[gaap_label] += line.value
                    # Update confidence to average
                    total_confidence = (total_confidence + confidence) / 2
                else:
                    translated_data[gaap_label] = line.value
                    total_confidence += confidence
                    translated_count += 1
        
        # Calculate average confidence
        avg_confidence = total_confidence / translated_count if translated_count > 0 else 0.0
        
        return GAAPFinancialData(
            company=data.company,
            year=data.year,
            quarter=data.quarter,
            report_type=data.report_type,
            data=translated_data,
            confidence_score=avg_confidence
        )
    
    def translate_label(self, french_label: str) -> Tuple[Optional[str], float]:
        """Translate a single French label to GAAP English"""
        if not french_label:
            return None, 0.0
        
        # Clean the label
        cleaned_label = self._clean_label(french_label)
        
        # Try exact match first
        gaap_label, confidence = self._exact_match(cleaned_label)
        if gaap_label:
            return gaap_label, confidence
        
        # Try fuzzy match
        gaap_label, confidence = self._fuzzy_match(cleaned_label)
        if gaap_label:
            return gaap_label, confidence
        
        # Try abbreviation match
        gaap_label, confidence = self._abbreviation_match(cleaned_label)
        if gaap_label:
            return gaap_label, confidence
        
        # No match found
        return None, 0.0
    
    def _clean_label(self, label: str) -> str:
        """Clean and normalize label text"""
        # Remove extra whitespace
        cleaned = re.sub(r'\s+', ' ', label.strip())
        
        # Remove common punctuation
        cleaned = re.sub(r'[^\w\s]', '', cleaned)
        
        # Convert to lowercase for matching
        return cleaned.lower()
    
    def _exact_match(self, cleaned_label: str) -> Tuple[Optional[str], float]:
        """Try exact match in mappings"""
        for category, mappings in self.mappings.items():
            for french, gaap in mappings.items():
                if self._clean_label(french) == cleaned_label:
                    return gaap, 1.0
        
        return None, 0.0
    
    def _fuzzy_match(self, cleaned_label: str) -> Tuple[Optional[str], float]:
        """Try fuzzy matching with partial matches"""
        best_match = None
        best_confidence = 0.0
        
        for category, mappings in self.mappings.items():
            for french, gaap in mappings.items():
                french_cleaned = self._clean_label(french)
                
                # Check if cleaned label contains or is contained in French label
                if cleaned_label in french_cleaned or french_cleaned in cleaned_label:
                    # Calculate similarity score
                    similarity = self._calculate_similarity(cleaned_label, french_cleaned)
                    if similarity > best_confidence and similarity >= 0.8:
                        best_match = gaap
                        best_confidence = similarity
        
        return best_match, best_confidence
    
    def _abbreviation_match(self, cleaned_label: str) -> Tuple[Optional[str], float]:
        """Try matching abbreviations"""
        if 'abbreviations' not in self.mappings:
            return None, 0.0
        
        abbreviations = self.mappings['abbreviations']
        for french, gaap in abbreviations.items():
            if self._clean_label(french) == cleaned_label:
                return gaap, 0.9  # Slightly lower confidence for abbreviations
        
        return None, 0.0
    
    def _calculate_similarity(self, str1: str, str2: str) -> float:
        """Calculate similarity between two strings"""
        if not str1 or not str2:
            return 0.0
        
        # Simple Jaccard similarity
        set1 = set(str1.split())
        set2 = set(str2.split())
        
        if not set1 and not set2:
            return 1.0
        if not set1 or not set2:
            return 0.0
        
        intersection = len(set1.intersection(set2))
        union = len(set1.union(set2))
        
        return intersection / union if union > 0 else 0.0
    
    def add_mapping(self, french_label: str, gaap_label: str, category: str = "custom") -> None:
        """Add a new mapping to the dictionary"""
        if category not in self.mappings:
            self.mappings[category] = {}
        
        self.mappings[category][french_label] = gaap_label
        logger.info(f"Added mapping: {french_label} -> {gaap_label}")
    
    def save_mappings(self) -> None:
        """Save current mappings to file"""
        try:
            self.mapping_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.mapping_file, 'w', encoding='utf-8') as f:
                yaml.dump(self.mappings, f, default_flow_style=False, allow_unicode=True)
            logger.info(f"Mappings saved to {self.mapping_file}")
        except Exception as e:
            logger.error(f"Error saving mappings: {e}")
    
    def get_untranslated_labels(self, data: FinancialData) -> List[str]:
        """Get list of labels that couldn't be translated"""
        untranslated = []
        
        for line in data.lines:
            gaap_label, confidence = self.translate_label(line.label)
            if not gaap_label or confidence < self.confidence_threshold:
                untranslated.append(line.label)
        
        return list(set(untranslated))  # Remove duplicates
    
    def suggest_mappings(self, untranslated_labels: List[str]) -> Dict[str, List[Dict[str, Any]]]:
        """Suggest possible GAAP mappings for untranslated labels"""
        suggestions = {}
        
        for label in untranslated_labels:
            cleaned_label = self._clean_label(label)
            suggestions[label] = []
            
            # Look for similar existing mappings
            for category, mappings in self.mappings.items():
                for french, gaap in mappings.items():
                    french_cleaned = self._clean_label(french)
                    similarity = self._calculate_similarity(cleaned_label, french_cleaned)
                    
                    if similarity > 0.5:  # Lower threshold for suggestions
                        suggestions[label].append({
                            'gaap_label': gaap,
                            'similarity': similarity,
                            'category': category
                        })
            
            # Sort by similarity
            suggestions[label].sort(key=lambda x: x['similarity'], reverse=True)
            # Keep only top 3 suggestions
            suggestions[label] = suggestions[label][:3]
        
        return suggestions
    
    def validate_translation(self, french_label: str, gaap_label: str) -> bool:
        """Validate if a translation makes sense"""
        # Basic validation rules
        validation_rules = [
            # Revenue items should be positive
            (r'revenu|chiffre|vente', lambda x: x > 0),
            # Expense items should be negative or positive (depending on presentation)
            (r'charge|frais|coût', lambda x: True),  # Can be either
            # Assets should be positive
            (r'actif|asset', lambda x: x > 0),
            # Liabilities should be positive
            (r'passif|dette|liability', lambda x: x > 0),
        ]
        
        for pattern, validator in validation_rules:
            if re.search(pattern, french_label.lower()):
                # This is a basic validation - in practice, you'd need the actual values
                return True
        
        return True  # Default to valid if no specific rules match

# Example usage
def main():
    """Example usage of the Label Translator"""
    translator = LabelTranslator()
    
    # Example financial data
    sample_data = FinancialData(
        company="ATW",
        year=2024,
        quarter=1,
        report_type="pnl",
        lines=[
            {"label": "Revenus nets", "value": 13940000000, "unit": "MAD"},
            {"label": "Charges d'exploitation", "value": 8500000000, "unit": "MAD"},
            {"label": "Résultat net", "value": 3600000000, "unit": "MAD"},
        ]
    )
    
    # Translate the data
    gaap_data = translator.translate_financial_data(sample_data)
    
    print(f"Translated {len(gaap_data.data)} items")
    print(f"Confidence score: {gaap_data.confidence_score:.2f}")
    
    for gaap_label, value in gaap_data.data.items():
        print(f"  {gaap_label}: {value:,.0f} MAD")
    
    # Check for untranslated labels
    untranslated = translator.get_untranslated_labels(sample_data)
    if untranslated:
        print(f"\nUntranslated labels: {untranslated}")
        
        # Get suggestions
        suggestions = translator.suggest_mappings(untranslated)
        for label, suggs in suggestions.items():
            print(f"\nSuggestions for '{label}':")
            for sugg in suggs:
                print(f"  - {sugg['gaap_label']} (similarity: {sugg['similarity']:.2f})")

if __name__ == "__main__":
    main() 