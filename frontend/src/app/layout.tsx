import "./global.css";
import "katex/dist/katex.min.css";
import ToastProvider from "@/components/providers/ToastProvider";
import NProgressWrapper from "@/lib/wrapper/nprogress.wrapper";

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>
        <NProgressWrapper>
          <ToastProvider>
            {children}
          </ToastProvider>
        </NProgressWrapper>
      </body>
    </html>
  );
}
