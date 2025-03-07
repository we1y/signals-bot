import type { Metadata } from "next";
import "@/assets/styles/globals.css";
import { ThemeProvider } from "@/providers/theme-provider";
import { MainProvider } from "@/providers/main-provider";
import { cookies } from "next/headers";
import Auth from "@/components/features/Auth";


export const metadata: Metadata = {
  title: "Mini App",
  description: "Mini App",
};

export default async function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  const cookieStore = await cookies();
  const token = cookieStore.get('auth')

  return (
    <html lang="en" suppressHydrationWarning>
      <head>
        <script src="https://telegram.org/js/telegram-web-app.js?56"></script>
      </head>
      <body
        className={`antialiased`}
      >
        <MainProvider>
          <ThemeProvider
            attribute='class'
            defaultTheme='light'
            enableSystem
            disableTransitionOnChange
          >
            {token ? children : <Auth />}
          </ThemeProvider>
        </MainProvider>
      </body>
    </html>
  );
}
