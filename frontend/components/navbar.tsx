"use client";

import Link from "next/link";
import { LogoSalesBot } from "@/app/icons";

export const Navbar = () => {
  return (
    <div className="p-2 flex flex-row gap-2 justify-between items-center border-b border-border">
      <Link href="/" className="flex items-center gap-2">
        <LogoSalesBot size={24} />
        <span className="font-semibold">Sales Bot</span>
      </Link>
    </div>
  );
};
