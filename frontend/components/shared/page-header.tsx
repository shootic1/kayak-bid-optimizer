import type * as React from 'react';

interface PageHeaderProps {
  readonly title: string;
  readonly description?: string;
}

/** Consistent page title + description block. */
export function PageHeader({ title, description }: PageHeaderProps): React.JSX.Element {
  return (
    <div className="mb-6 space-y-1">
      <h1 className="text-2xl font-semibold tracking-tight">{title}</h1>
      {description ? <p className="text-muted-foreground text-sm">{description}</p> : null}
    </div>
  );
}
