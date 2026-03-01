type WorkerDraft = {
  name: string;
};

const emptyDraft = (): WorkerDraft => ({
  name: '',
});

export function useWorkerDraft() {
  const draft = useState<WorkerDraft>('worker:draft', () => emptyDraft());

  const resetDraft = () => {
    draft.value = emptyDraft();
  };

  const hasDraft = computed(() => {
    const d = draft.value;
    return (d.name ?? '').toString().trim().length > 0;
  });

  return { draft, resetDraft, hasDraft };
}
