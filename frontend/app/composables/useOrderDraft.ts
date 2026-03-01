type OrderDraft = {
  name: string;
  start: string;
  end: string;
  target: string | number;
  product: string;
  status: string;
  priority: string;
  comments: string;
};

const emptyDraft = (): OrderDraft => ({
  name: '',
  start: '',
  end: '',
  target: '',
  product: '',
  status: 'Planned',
  priority: 'Medium',
  comments: '',
});

export function useOrderDraft() {
  const draft = useState<OrderDraft>('order:draft', () => emptyDraft());

  const resetDraft = () => {
    draft.value = emptyDraft();
  };

  const hasDraft = computed(() => {
    const d = draft.value;
    return (
      (d.name ?? '').toString().trim().length > 0 ||
      (d.start ?? '').toString().trim().length > 0 ||
      (d.end ?? '').toString().trim().length > 0 ||
      (d.target ?? '').toString().trim().length > 0 ||
      (d.product ?? '').toString().trim().length > 0 ||
      (d.status ?? '').toString().trim().length > 0 ||
      (d.priority ?? '').toString().trim().length > 0 ||
      (d.comments ?? '').toString().trim().length > 0
    );
  });

  return { draft, resetDraft, hasDraft };
}
