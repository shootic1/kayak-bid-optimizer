import type * as React from 'react';

import { cn } from '@/lib/utils';

interface SeparatorProps extends React.HTMLAttributes<HTMLDivElement> {
  orientation?: 'horizontal' | 'vertical';
}

function Separator({
  className,
  orientation = 'horizontal',
  ...props
}: SeparatorProps): React.JSX.Element {
  return (
    <div
      role="separator"
      aria-orientation={orientation}
      className={cn(
        'bg-border shrink-0',
        orientation === 'horizontal' ? 'h-px w-full' : 'h-full w-px',
        className,
      )}
      {...props}
    />
  );
}

export { Separator };
