import React from "react";
import Link from "next/link";
import { cn } from "@/lib/utils"
import { cva, type VariantProps } from "class-variance-authority"

interface CustomLinkProps extends React.AnchorHTMLAttributes<HTMLAnchorElement> {
    className?: string;
    href: string; // Make href required
  }

  const linkVariants = cva(
    "inline-flex items-center justify-center gap-2 whitespace-nowrap rounded-md text-sm font-bold transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring disabled:pointer-events-none disabled:opacity-50 [&_svg]:pointer-events-none [&_svg]:size-4 [&_svg]:shrink-0",
    {
      variants: {
        variant: {
          default:
            "bg-primary text-primary-foreground shadow hover:bg-primary/90",
          destructive:
            "bg-destructive text-destructive-foreground shadow-sm hover:bg-destructive/90",
          outline:
            "border border-input bg-background shadow-sm hover:bg-accent hover:text-accent-foreground",
          secondary:
            "bg-secondary text-secondary-foreground shadow-sm hover:bg-secondary/80",
          ghost: "hover:bg-accent hover:text-accent-foreground",
          link: "text-primary underline-offset-4 hover:underline",
        },
        size: {
          default: "h-9 px-4 py-2",
          sm: "h-8 rounded-md px-3 text-xs",
          lg: "h-10 rounded-md px-8",
          icon: "h-9 w-9",
        },
      },
      defaultVariants: {
        variant: "default",
        size: "default",
      },
    }
  )

const CustomLink = React.forwardRef<HTMLLinkElement, CustomLinkProps>(
    ({ className, href, ...props }, ref) => (
      <Link
        href={href}
        className={cn(linkVariants(), className)}
        ref={ref as React.Ref<HTMLAnchorElement>}
        {...props}
      />
    )
  );

export default CustomLink;