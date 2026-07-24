import type { Metadata, Viewport } from 'next';

import { APP_NAME } from '@kayak/shared';

import { AppShell } from '@/components/shared/app-shell';
import { ThemeProvider } from '@/components/shared/theme-provider';

import '@/styles/globals.css';

export const metadata: Metadata = {
  title: {
    default: APP_NAME,
    template: `%s · ${APP_NAME}`,
  },
  description: 'Internal OTA tool for optimizing KAYAK Inline and Dynamic Inline Ad bids.',
  applicationName: APP_NAME,
};

export const viewport: Viewport = {
  themeColor: [
    { media: '(prefers-color-scheme: light)', color: '#ffffff' },
    { media: '(prefers-color-scheme: dark)', color: '#0b1120' },
  ],
};

export default function RootLayout({
  children,
}: Readonly<{ children: React.ReactNode }>): React.JSX.Element {
  return (
    <html lang="en" suppressHydrationWarning>
      <body className="bg-background text-foreground min-h-svh font-sans antialiased">
        <ThemeProvider
          attribute="class"
          defaultTheme="system"
          enableSystem
          disableTransitionOnChange
        >
          <AppShell>{children}</AppShell>
        </ThemeProvider>
      </body>
    </html>
  );
}
