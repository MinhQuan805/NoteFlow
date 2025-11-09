// app/layout.tsx
'use client';

export default function RootLayout({ children }: { children: React.ReactNode }) {

  return (
    <div>
      <main>{children}</main>
    </div>
  );
}