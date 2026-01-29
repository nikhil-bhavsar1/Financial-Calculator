import React from 'react';
import { Zap, Cpu, Clock, AlertCircle, Trash2 } from 'lucide-react';
import { OllamaModel } from '../hooks/useLocalLLM';

interface ModelSelectorProps {
    models: OllamaModel[];
    selectedModel: string;
    currentlyLoaded: OllamaModel | null;
    onSelect: (modelName: string) => void;
    onUnload: (modelName: string) => void;
    disabled?: boolean;
}

export const ModelSelector: React.FC<ModelSelectorProps> = ({
    models,
    selectedModel,
    currentlyLoaded,
    onSelect,
    onUnload,
    disabled
}) => {
    const selectedIsLoaded = selectedModel === currentlyLoaded?.name;

    return (
        <div className="space-y-2">
            <div className="flex items-center justify-between">
                <label className="text-sm font-medium text-gray-700">
                    Active Model
                    {currentlyLoaded && (
                        <span className="ml-2 text-xs text-green-600 flex items-center inline-flex">
                            <Zap size={12} className="mr-1" />
                            {currentlyLoaded.name} in GPU
                        </span>
                    )}
                </label>

                {selectedIsLoaded ? (
                    <span className="text-xs bg-green-100 text-green-800 px-2 py-1 rounded-full flex items-center">
                        <Zap size={10} className="mr-1" /> Loaded
                    </span>
                ) : selectedModel ? (
                    <span className="text-xs bg-yellow-100 text-yellow-800 px-2 py-1 rounded-full flex items-center">
                        <AlertCircle size={10} className="mr-1" /> Cold Start
                    </span>
                ) : null}
            </div>

            <select
                value={selectedModel}
                onChange={(e) => onSelect(e.target.value)}
                disabled={disabled}
                className="w-full p-2 border rounded-lg bg-white disabled:opacity-50"
            >
                <option value="">Select a model...</option>

                {/* Currently Loaded Group */}
                {currentlyLoaded && (
                    <optgroup label="⚡ Currently in GPU Memory">
                        <option value={currentlyLoaded.name}>
                            {currentlyLoaded.name} ({currentlyLoaded.vram_usage})
                        </option>
                    </optgroup>
                )}

                {/* Available Models */}
                <optgroup label={currentlyLoaded ? "Available (Disk)" : "Available Models"}>
                    {models
                        .filter(m => !m.loaded)
                        .map(model => (
                            <option key={model.name} value={model.name}>
                                {model.name}
                                {model.parameter_size && ` (${model.parameter_size})`}
                                {model.quantization_level && ` [${model.quantization_level}]`}
                            </option>
                        ))}
                </optgroup>
            </select>

            {/* Model Details Panel */}
            {currentlyLoaded && (
                <div className="mt-2 p-3 bg-green-50 border border-green-200 rounded-lg text-sm">
                    <div className="flex items-center justify-between mb-1">
                        <span className="font-semibold text-green-900 flex items-center">
                            <Cpu size={14} className="mr-1" />
                            GPU Active
                        </span>
                        <button
                            onClick={() => onUnload(currentlyLoaded.name)}
                            className="text-red-600 hover:text-red-800 flex items-center text-xs"
                            title="Unload from GPU (free VRAM)"
                        >
                            <Trash2 size={12} className="mr-1" /> Eject
                        </button>
                    </div>
                    <div className="text-green-800 space-y-1">
                        <p>VRAM Usage: {currentlyLoaded.vram_usage}</p>
                        {currentlyLoaded.expires_at && (
                            <p className="flex items-center text-xs">
                                <Clock size={12} className="mr-1" />
                                Expires: {new Date(currentlyLoaded.expires_at).toLocaleTimeString()}
                            </p>
                        )}
                    </div>
                </div>
            )}

            {!currentlyLoaded && selectedModel && (
                <div className="mt-2 p-3 bg-yellow-50 border border-yellow-200 rounded-lg text-sm text-yellow-800">
                    <AlertCircle size={14} className="inline mr-1" />
                    Model will load into GPU on first message (may take 1-10s)
                </div>
            )}
        </div>
    );
};
