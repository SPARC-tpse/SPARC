type OrderDraft = {
  name: string;
  start_date: string;
  end_date: string;
  target_amount: number;
  product_name: string;
  status: number;
  priority: number;
  comments: string;
};

const emptyDraft = (): OrderDraft => ({
  name: '',
  start_date: '',
  end_date: '',
  target_amount: 0,
  product_name: '',
  status: 0,
  priority: 1,
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
      (d.start_date ?? '').toString().trim().length > 0 ||
      (d.end_date ?? '').toString().trim().length > 0 ||
      (d.target_amount ?? '').toString().trim().length > 0 ||
      (d.product_name ?? '').toString().trim().length > 0 ||
      (d.status ?? '').toString().trim().length > 0 ||
      (d.priority ?? '').toString().trim().length > 0 ||
      (d.comments ?? '').toString().trim().length > 0
    );
  });

  return { draft, resetDraft, hasDraft };
}
