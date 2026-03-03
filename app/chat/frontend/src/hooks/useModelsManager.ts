import { useCallback, useEffect, useMemo, useState, useRef } from 'react';
import { Model } from '../types';
import { MODEL_META } from '../constants';
import { usePersistedSetting } from './usePersistedSetting';

interface ModelsApiModel {
  id: string;
  name?: string;
  type?: string;
  priority?: number;
  context_length?: number;
  default?: boolean;
}

interface ModelsApiResponse {
  models: ModelsApiModel[];
}

export function useModelsManager() {
  const [modelsData, setModelsData] = useState<Model[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [loadError, setLoadError] = useState<string | null>(null);

  // Multi-model selection (for Compare, Analyze, Debate, Personalities)
  const [persistedSelected, setPersistedSelected] = usePersistedSetting<string[] | null>('playground_selected_models', null);
  const isSelectionInitialized = useRef(persistedSelected !== null);

  // Chat mode uses a separate, independent model selection
  const [chatModelId, setChatModelId] = usePersistedSetting<string | null>('playground_chat_model', null);
  const isChatModelInitialized = useRef(chatModelId !== null);

  const selected = useMemo(() => persistedSelected ?? [], [persistedSelected]);

  const setSelected = useCallback((value: string[] | ((prev: string[]) => string[])) => {
    setPersistedSelected(prev => {
      const safePrev = prev ?? [];
      return typeof value === 'function' ? value(safePrev) : value;
    });
  }, [setPersistedSelected]);

  const [moderator, setModerator] = useState<string>('');

  const loadModels = useCallback(async (): Promise<void> => {
    setIsLoading(true);
    setLoadError(null);

    try {
      const response = await fetch('/models.json');
      if (!response.ok) throw new Error(`HTTP ${response.status}`);

      const data: ModelsApiResponse = await response.json();
      if (!data.models?.length) throw new Error('No models in models.json');

      const apiModels = data.models
        .filter((model) => model.type !== 'external')
        .map((model) => {
          const modelType: 'self-hosted' | 'github' =
            (model.type === 'github' || model.type === 'api') ? 'github' : 'self-hosted';
          const meta = MODEL_META[modelType];
          return {
            id: model.id,
            name: meta.name || model.name || model.id,
            color: meta.color,
            type: modelType,
            response: '',
            priority: model.priority,
            context_length: model.context_length,
            default: model.default,
          };
        });

      setModelsData(apiModels);
      setIsLoading(false);

      if (!isSelectionInitialized.current) {
        setPersistedSelected([]);
        isSelectionInitialized.current = true;
      }

      // Initialize chat model: gpt-4o > default > first github > first available
      if (!isChatModelInitialized.current) {
        const gpt4o = apiModels.find(m => m.id === 'openai/gpt-4o');
        const defaultModel = apiModels.find(m => m.default);
        const firstApiModel = apiModels.find(m => m.type === 'github');
        setChatModelId(gpt4o?.id ?? defaultModel?.id ?? firstApiModel?.id ?? apiModels[0]?.id ?? null);
        isChatModelInitialized.current = true;
      }

      // Set moderator: prefer github model, then default, then first available
      const moderatorId = apiModels.find(m => m.type === 'github')?.id
        ?? apiModels.find(m => m.default)?.id
        ?? apiModels[0]?.id
        ?? '';
      setModerator(moderatorId);

    } catch {
      setIsLoading(false);
      setLoadError('Could not load models');
    }
  }, [setPersistedSelected, setChatModelId]);

  const retryNow = useCallback(() => {
    loadModels();
  }, [loadModels]);

  useEffect(() => {
    loadModels();
  }, [loadModels]);

  const availableModels = useMemo(
    () => modelsData.filter(m => !selected.includes(m.id)),
    [modelsData, selected],
  );

  const { totalModelsByType, allSelectedByType } = useMemo(() => {
    const total = {
      'self-hosted': modelsData.filter(m => m.type === 'self-hosted').length,
      github: modelsData.filter(m => m.type === 'github').length,
    };
    const selectedCount = {
      'self-hosted': modelsData.filter(m => m.type === 'self-hosted' && selected.includes(m.id)).length,
      github: modelsData.filter(m => m.type === 'github' && selected.includes(m.id)).length,
    };

    return {
      totalModelsByType: total,
      allSelectedByType: {
        'self-hosted': total['self-hosted'] > 0 && selectedCount['self-hosted'] === total['self-hosted'],
        github: total.github > 0 && selectedCount.github === total.github,
      } as Record<'self-hosted' | 'github', boolean>,
    };
  }, [modelsData, selected]);

  const modelIdToName = useCallback(
    (id: string) => modelsData.find(m => m.id === id)?.name || id,
    [modelsData],
  );

  const getModelEndpoints = useCallback((models: Model[]): Record<string, string> => {
    const endpoints: Record<string, string> = {};
    const isDev = window.location.hostname === 'localhost';

    const subdomainMap: Record<string, string> = {
      'qwen3-4b': 'qwen',
      'phi-4-mini': 'phi',
      'functiongemma-270m-it': 'functiongemma',
      'smollm3-3b': 'smollm3',
      'lfm2.5-1.2b-instruct': 'lfm2',
      'dasd-4b-thinking': 'dasd',
      'agentcpm-explore-4b': 'agentcpm',
      'gemma-3-12b-it': 'gemma',
      'llama-3.2-3b': 'llama',
      'mistral-7b-instruct-v0.3': 'mistral',
      'rnj-1-instruct': 'rnj',
      'deepseek-r1-distill-qwen-1.5b': 'r1qwen',
      'nanbeige4-3b-thinking': 'nanbeige',
      'glm-4.7-flash': 'glm',
      'gpt-oss-20b': 'gptoss',
    };

    const portMap: Record<string, number> = {
      'qwen3-4b': 8100,
      'phi-4-mini': 8101,
      'functiongemma-270m-it': 8103,
      'smollm3-3b': 8104,
      'lfm2.5-1.2b-instruct': 8105,
      'dasd-4b-thinking': 8106,
      'agentcpm-explore-4b': 8107,
      'gemma-3-12b-it': 8200,
      'llama-3.2-3b': 8201,
      'mistral-7b-instruct-v0.3': 8202,
      'rnj-1-instruct': 8203,
      'deepseek-r1-distill-qwen-1.5b': 8300,
      'nanbeige4-3b-thinking': 8301,
      'glm-4.7-flash': 8302,
      'gpt-oss-20b': 8303,
    };

    models.forEach(model => {
      if (model.type === 'self-hosted') {
        if (isDev) {
          const port = portMap[model.id] || 8000;
          endpoints[model.id] = `http://localhost:${port}/v1`;
        } else {
          const subdomain = subdomainMap[model.id];
          if (subdomain) {
            endpoints[model.id] = `https://${subdomain}.neevs.io/v1`;
          }
        }
      } else if (model.type === 'github') {
        endpoints[model.id] = 'https://models.github.ai/inference';
      }
    });

    return endpoints;
  }, []);

  return {
    modelsData,
    setModelsData,
    selected,
    setSelected,
    chatModelId,
    setChatModelId,
    moderator,
    setModerator,
    availableModels,
    totalModelsByType,
    allSelectedByType,
    modelIdToName,
    isLoading,
    loadError,
    retryNow,
    getModelEndpoints,
  };
}
