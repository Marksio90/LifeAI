import type { ReactNode } from "react";
import { AuthProvider } from "@/contexts/AuthContext";
import { ThemeProvider } from "@/contexts/ThemeContext";
import { Toaster } from "react-hot-toast";
import "./globals.css";

export const metadata = {
  title: "LifeAI - Multi-Agent AI Platform",
  description: "Wieloagentowa platforma AI wspierająca użytkowników w życiu codziennym",
};

export default function RootLayout({
  children,
}: {
  children: ReactNode;
}) {
  return (
    <html lang="pl" suppressHydrationWarning>
      <body>
        <ThemeProvider>
          <AuthProvider>
            {children}
            <Toaster
              position="top-right"
              toastOptions={{
                duration: 4000,
                style: {
                  background: 'var(--toast-bg)',
                  color: 'var(--toast-text)',
                },
                success: {
                  iconTheme: {
                    primary: '#10b981',
                    secondary: 'white',
                  },
                },
                error: {
                  iconTheme: {
                    primary: '#ef4444',
                    secondary: 'white',
                  },
                },
              }}
            />
          </AuthProvider>
        </ThemeProvider>
      </body>
    </html>
  );
}
