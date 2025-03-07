import { useEffect } from "react";

export default function BackButton () {
    useEffect(() => {
        const tg = window.Telegram.WebApp;
        
        // Enable the back button
        tg.BackButton.show();
    
        // Handle back button click
        tg.BackButton.onClick(() => {
          // You can customize this behavior
          tg.BackButton.hide();
          window.history.back();
        });
    
        // Cleanup on component unmount
        return () => {
          tg.BackButton.hide();
          tg.BackButton.offClick();
        };
      }, []);
    
      return null;
}