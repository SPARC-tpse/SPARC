type ResourceDraft = {
  name: string;
  type: string;
  status: string;
};

const emptyDraft = (): ResourceDraft => ({
  name: '',
  type: 'Machinery',
  status: 'available',
});

export function useResourceDraft() {
  const draft = useState<ResourceDraft>('resource:draft', () => emptyDraft());

  const resetDraft = () => {
    draft.value = emptyDraft();
  };

  const hasDraft = computed(() => {
    const d = draft.value;
    return (
      (d.name ?? '').toString().trim().length > 0 ||
      (d.type ?? '').toString().trim().length > 0 ||
      (d.status ?? '').toString().trim().length > 0
    );
  });

  return { draft, resetDraft, hasDraft };
}
