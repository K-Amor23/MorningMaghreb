import React from 'react'
import { CheckCircleIcon, ExclamationTriangleIcon, InformationCircleIcon } from '@heroicons/react/24/outline'

interface DataQualityBadgeProps {
    quality: 'Partial' | 'Complete'
    size?: 'sm' | 'md' | 'lg' | 'xl'
    showIcon?: boolean
    showTooltip?: boolean
    className?: string
    variant?: 'default' | 'prominent' | 'minimal'
}

const DataQualityBadge: React.FC<DataQualityBadgeProps> = ({
    quality,
    size = 'md',
    showIcon = true,
    showTooltip = true,
    className = '',
    variant = 'default'
}) => {
    const isComplete = quality === 'Complete'

    // Size configurations
    const sizes = {
        sm: {
            badge: 'px-2 py-1 text-xs',
            icon: 'w-3 h-3'
        },
        md: {
            badge: 'px-3 py-1.5 text-sm',
            icon: 'w-4 h-4'
        },
        lg: {
            badge: 'px-4 py-2 text-base',
            icon: 'w-5 h-5'
        },
        xl: {
            badge: 'px-6 py-3 text-lg font-semibold',
            icon: 'w-6 h-6'
        }
    }

    // Variant configurations
    const variants = {
        default: {
            complete: 'bg-green-100 text-green-800 border border-green-200',
            partial: 'bg-yellow-100 text-yellow-800 border border-yellow-200'
        },
        prominent: {
            complete: 'bg-green-500 text-white shadow-lg',
            partial: 'bg-yellow-500 text-white shadow-lg'
        },
        minimal: {
            complete: 'bg-green-50 text-green-700',
            partial: 'bg-yellow-50 text-yellow-700'
        }
    }

    const sizeConfig = sizes[size]
    const variantConfig = variants[variant]
    const colorConfig = isComplete ? variantConfig.complete : variantConfig.partial

    const baseClasses = `inline-flex items-center gap-1.5 rounded-full font-medium transition-all duration-200 ${sizeConfig.badge} ${colorConfig} ${className}`

    const iconClasses = `${sizeConfig.icon} ${isComplete ? 'text-green-600' : 'text-yellow-600'}`

    const tooltipText = isComplete
        ? 'Complete data available - all recent information is up to date'
        : 'Partial data available - some information may be outdated or incomplete'

    const badgeContent = (
        <>
            {showIcon && (
                isComplete ? (
                    <CheckCircleIcon className={iconClasses} />
                ) : (
                    <ExclamationTriangleIcon className={iconClasses} />
                )
            )}
            <span className="font-medium">{quality}</span>
            {showTooltip && (
                <InformationCircleIcon className={`${sizeConfig.icon} opacity-60`} />
            )}
        </>
    )

    if (showTooltip) {
        return (
            <div className="group relative inline-block">
                <span className={baseClasses}>
                    {badgeContent}
                </span>
                <div className="absolute bottom-full left-1/2 transform -translate-x-1/2 mb-2 px-3 py-2 text-sm text-white bg-gray-900 rounded-lg opacity-0 group-hover:opacity-100 transition-opacity duration-200 pointer-events-none whitespace-nowrap z-50">
                    {tooltipText}
                    <div className="absolute top-full left-1/2 transform -translate-x-1/2 w-0 h-0 border-l-4 border-r-4 border-t-4 border-transparent border-t-gray-900"></div>
                </div>
            </div>
        )
    }

    return (
        <span className={baseClasses}>
            {badgeContent}
        </span>
    )
}

export default DataQualityBadge 