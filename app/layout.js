import './globals.css';

export const metadata = {
  title: 'MetaBid Copilot',
  description: 'Affiliate ads bid and ROI copilot',
};

export default function RootLayout({ children }) {
  return (
    <html lang="it">
      <body>{children}</body>
    </html>
  );
}
