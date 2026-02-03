import React from 'react';
import { CheckCircle2, AlertCircle, Info, AlertTriangle } from 'lucide-react';

export interface IndASStatus {
    isIndASDocument: boolean;
    isStandalone: boolean;
    isConsolidated: boolean;
    confidence: number;
    warnings?: string[];
    validationErrors?: number;
}

interface IndASStatusIndicatorProps {
    status: IndASStatus;
    className?: string;
    showDetails?: boolean;
}

export const IndASStatusIndicator: React.FC<IndASStatusIndicatorProps> = ({
    status,
    className = '',
    showDetails = false
}) => {
    const { isIndASDocument, confidence, warnings, validationErrors } = status;

    const getStatusColor = () => {
        if (!isIndASDocument) return 'gray';
        if (confidence >= 0.8) return 'green';
        if (confidence >= 0.6) return 'blue';
        if (confidence >= 0.4) return 'yellow';
        return 'red';
    };

    const getStatusColorClass = () => {
        const color = getStatusColor();
        switch (color) {
            case 'green':
                return 'bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-400 border-green-200 dark:border-green-800';
            case 'blue':
                return 'bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-400 border-blue-200 dark:border-blue-800';
            case 'yellow':
                return 'bg-yellow-100 dark:bg-yellow-900/30 text-yellow-700 dark:text-yellow-400 border-yellow-200 dark:border-yellow-800';
            case 'red':
                return 'bg-red-100 dark:bg-red-900/30 text-red-700 dark:text-red-400 border-red-200 dark:border-red-800';
            default:
                return 'bg-gray-100 dark:bg-slate-900/30 text-gray-700 dark:text-gray-400 border-gray-200 dark:border-slate-800';
        }
    };

    const getStatusText = () => {
        if (!isIndASDocument) return 'Non-Ind AS Document';
        if (confidence >= 0.8) return 'High Confidence Ind AS';
        if (confidence >= 0.6) return 'Good Confidence Ind AS';
        if (confidence >= 0.4) return 'Moderate Confidence Ind AS';
        return 'Low Confidence Ind AS';
    };

    return (
        <div className={`ind-as-status ${className}`}>
            <div className={`flex items-center gap-3 px-4 py-3 rounded-lg border ${getStatusColorClass()}`}>
                {/* Status Icon */}
                <div className="flex items-center gap-2">
                    {getStatusIcon()}
                    <div>
                        <div className="text-sm font-semibold">
                            {getStatusText()}
                        </div>
                        {isIndASDocument && (
                            <div className="text-xs text-gray-600 dark:text-gray-400">
                                Confidence: {(confidence * 100).toFixed(0)}%
                            </div>
                        )}
                    </div>
                </div>

                {/* Document Type Badges */}
                {isIndASDocument && (
                    <div className="flex items-center gap-2">
                        {status.isStandalone && (
                            <span className="px-2 py-1 bg-purple-100 dark:bg-purple-900/30 text-purple-700 dark:text-purple-400 text-xs font-medium rounded-full">
                                Standalone
                            </span>
                        )}
                        {status.isConsolidated && (
                            <span className="px-2 py-1 bg-orange-100 dark:bg-orange-900/30 text-orange-700 dark:text-orange-400 text-xs font-medium rounded-full">
                                Consolidated
                            </span>
                        )}
                    </div>
                )}
            </div>

            {/* Warnings and Errors */}
            {(showDetails || warnings?.length > 0 || validationErrors) && (
                <div className="mt-3 space-y-2">
                    {warnings && warnings.length > 0 && (
                        <div className="flex items-start gap-2 p-3 bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800 rounded-lg">
                            <AlertTriangle className="w-4 h-4 text-yellow-600 dark:text-yellow-400 mt-0.5 flex-shrink-0" />
                            <div className="flex-1">
                                <div className="text-sm font-semibold text-yellow-800 dark:text-yellow-200">
                                    Ind AS Warnings ({warnings.length})
                                </div>
                                <div className="mt-1 space-y-1">
                                    {warnings.slice(0, 3).map((warning, idx) => (
                                        <div key={idx} className="text-xs text-yellow-700 dark:text-yellow-300">
                                            • {warning}
                                        </div>
                                    ))}
                                    {warnings.length > 3 && (
                                        <div className="text-xs text-yellow-700 dark:text-yellow-300">
                                            • And {warnings.length - 3} more...
                                        </div>
                                    )}
                                </div>
                            </div>
                        </div>
                    )}

                    {validationErrors !== undefined && (
                        <div className={`flex items-start gap-2 p-3 rounded-lg border ${
                            validationErrors > 0
                                ? 'bg-red-50 dark:bg-red-900/20 border-red-200 dark:border-red-800'
                                : 'bg-green-50 dark:bg-green-900/20 border-green-200 dark:border-green-800'
                        }`}>
                            {validationErrors > 0 ? (
                                <>
                                    <AlertCircle className="w-4 h-4 text-red-600 dark:text-red-400 mt-0.5 flex-shrink-0" />
                                    <div className="flex-1">
                                        <div className="text-sm font-semibold text-red-800 dark:text-red-200">
                                            {validationErrors} Validation Error{validationErrors !== 1 ? 's' : ''}
                                        </div>
                                        <div className="text-xs text-red-700 dark:text-red-300">
                                            Some mandatory Ind AS checks failed
                                        </div>
                                    </div>
                                </>
                            ) : (
                                <>
                                    <CheckCircle2 className="w-4 h-4 text-green-600 dark:text-green-400 mt-0.5 flex-shrink-0" />
                                    <div className="flex-1">
                                        <div className="text-sm font-semibold text-green-800 dark:text-green-200">
                                            All Checks Passed
                                        </div>
                                        <div className="text-xs text-green-700 dark:text-green-300">
                                            Document passes all mandatory Ind AS validations
                                        </div>
                                    </div>
                                </>
                            )}
                        </div>
                    )}
                </div>
            )}

            {/* Info Icon */}
            <div className="flex items-center gap-1 text-xs text-gray-500 dark:text-gray-400">
                <Info className="w-3 h-3" />
                <span>Ind AS: Indian Accounting Standards</span>
            </div>
        </div>
    );
};

function getStatusIcon() {
    return (
        <div className="w-8 h-8 rounded-full flex items-center justify-center bg-white dark:bg-slate-800 shadow-md">
            <CheckCircle2 className="w-5 h-5 text-green-600 dark:text-green-400" />
        </div>
    );
}

export default IndASStatusIndicator;