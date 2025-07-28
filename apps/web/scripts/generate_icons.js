const fs = require('fs');
const path = require('path');

// Create a simple SVG icon
const createSVGIcon = (size) => {
    return `<svg width="${size}" height="${size}" viewBox="0 0 ${size} ${size}" xmlns="http://www.w3.org/2000/svg">
    <rect width="${size}" height="${size}" fill="#1e40af"/>
    <text x="50%" y="50%" text-anchor="middle" dy=".3em" fill="white" font-family="Arial, sans-serif" font-size="${size * 0.4}">CI</text>
  </svg>`;
};

// Convert SVG to data URL
const svgToDataURL = (svg) => {
    return `data:image/svg+xml;base64,${Buffer.from(svg).toString('base64')}`;
};

// Create icons directory if it doesn't exist
const iconsDir = path.join(__dirname, '../public/icons');
if (!fs.existsSync(iconsDir)) {
    fs.mkdirSync(iconsDir, { recursive: true });
}

// Generate basic icons
const sizes = [32, 72, 96, 128, 144, 152, 180, 192, 384, 512];

sizes.forEach(size => {
    const svg = createSVGIcon(size);
    const dataURL = svgToDataURL(svg);

    // For now, just create empty files - in a real scenario you'd convert SVG to PNG
    const filename = `icon-${size}x${size}.png`;
    fs.writeFileSync(path.join(iconsDir, filename), '');
    console.log(`Created ${filename}`);
});

console.log('Icon generation complete!'); 