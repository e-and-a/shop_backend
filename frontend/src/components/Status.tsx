export function LoadingState({ text = "Загрузка..." }: { text?: string }) {
  return <div className="page-status">{text}</div>;
}

export function ErrorState({ message }: { message: string }) {
  return <div className="alert error">{message}</div>;
}

export function EmptyState({ title, text }: { title: string; text?: string }) {
  return (
    <div className="empty-state">
      <h3>{title}</h3>
      {text && <p>{text}</p>}
    </div>
  );
}
