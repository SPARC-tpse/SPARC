type DisruptionDraft = {
  name: string;
  start: string;
  end: string;
  resource: string | number;
  type: string | number;
};

const emptyDraft = (): DisruptionDraft => ({
  name: '',
  start: '',
  end: '',
  resource: '',
  type: '',
});

export function useDisruptionDraft() {
  // Global/persistenter Draft über Routenwechsel hinweg
  const draft = useState<DisruptionDraft>('disruption:draft', () => emptyDraft());

  const resetDraft = () => {
    draft.value = emptyDraft();
  };

  const hasDraft = computed(() => {
    const d = draft.value;
    return (
      (d.name ?? '').toString().trim().length > 0 ||
      (d.start ?? '').toString().trim().length > 0 ||
      (d.end ?? '').toString().trim().length > 0 ||
      (d.resource ?? '').toString().trim().length > 0 ||
      (d.type ?? '').toString().trim().length > 0
    );
  });

  return { draft, resetDraft, hasDraft };
}