import { motion } from "framer-motion";

import { MessageIcon } from "./icons";
import { LogoSalesBot } from "@/app/icons";

export const Overview = () => {
  return (
    <motion.div
      key="overview"
      className="max-w-3xl mx-auto md:mt-20"
      initial={{ opacity: 0, scale: 0.98 }}
      animate={{ opacity: 1, scale: 1 }}
      exit={{ opacity: 0, scale: 0.98 }}
      transition={{ delay: 0.5 }}
    >
      <div className="rounded-xl p-6 flex flex-col gap-8 leading-relaxed text-center max-w-xl">
        <p className="flex flex-row justify-center gap-4 items-center">
          <LogoSalesBot size={32} />
          <span>+</span>
          <MessageIcon size={32} />
        </p>
        <p>
          Welcome to <span className="font-medium">Sales Bot</span>, your
          AI-powered customer support assistant. I can help you with:
        </p>
        <ul className="text-left list-disc list-inside space-y-2 text-muted-foreground">
          <li>Product inquiries and recommendations</li>
          <li>Order tracking and status updates</li>
          <li>Return and refund policies</li>
          <li>General support questions</li>
        </ul>
        <p className="text-muted-foreground">
          Just type your question below to get started!
        </p>
      </div>
    </motion.div>
  );
};
