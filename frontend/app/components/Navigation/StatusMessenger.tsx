"use client";

import React, { useState, useEffect } from "react";
import { StatusMessage } from "@/app/types";
import { motion, AnimatePresence } from "framer-motion";

import { FaWandMagicSparkles } from "react-icons/fa6";
import { IoWarning } from "react-icons/io5";
import { BiSolidMessageAltDetail } from "react-icons/bi";
import { BiSolidErrorCircle } from "react-icons/bi";

interface StatusMessengerProps {
  status_messages: StatusMessage[];
  set_status_messages: (messages: StatusMessage[]) => void;
}

const StatusMessengerComponent: React.FC<StatusMessengerProps> = ({
  status_messages,
  set_status_messages,
}) => {
  const [messages, setMessages] = useState<StatusMessage[]>([]);

  useEffect(() => {
    if (status_messages.length > 0) {
      // Add new messages to the state
      setMessages((prevMessages) => [...prevMessages, ...status_messages]);

      // Clear the status_messages
      set_status_messages([]);
    }

    // Clear messages older than 5 seconds
    const interval = setInterval(() => {
      const currentTime = new Date().getTime();
      setMessages((prevMessages) =>
        prevMessages.filter((message) => {
          const messageTime = new Date(message.timestamp).getTime();
          return currentTime - messageTime < 5000;
        })
      );
    }, 1000); // Check every second

    return () => clearInterval(interval);
  }, [status_messages, set_status_messages]);

  const getMessageColor = (type: string) => {
    switch (type) {
      case "INFO":
        return "bg-button-verba";
      case "WARNING":
        return "bg-secondary-verba";
      case "SUCCESS":
        return "bg-primary-verba";
      case "ERROR":
        return "bg-warning-verba";
      default:
        return "bg-button-verba";
    }
  };

  const getMessageIcon = (type: string) => {
    const icon_size = 15;

    switch (type) {
      case "INFO":
        return <BiSolidMessageAltDetail size={icon_size} />;
      case "WARNING":
        return <IoWarning size={icon_size} />;
      case "SUCCESS":
        return <FaWandMagicSparkles size={icon_size} />;
      case "ERROR":
        return <BiSolidErrorCircle size={icon_size} />;
      default:
        return <BiSolidMessageAltDetail size={icon_size} />;
    }
  };

  return (
    <div className="fixed bottom-4 right-4 space-y-2">
      <AnimatePresence>
        {messages
          .filter((message) => {
            const messageTime = new Date(message.timestamp).getTime();
            const currentTime = new Date().getTime();
            return currentTime - messageTime < 5000; // 5 seconds in milliseconds
          })
          .map((message, index) => (
            <motion.div
              key={index}
              initial={{ opacity: 0, y: 50 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: 50 }}
              className={`${getMessageColor(message.type)} text-text-verba p-4 min-w-[300px] rounded-lg z-10 shadow-md`}
            >
              <div className="flex flex-col gap-2">
                <div className="flex flex-row gap-2 items-center">
                  {getMessageIcon(message.type)}
                  <p className="text-xs font-bold">{message.type}</p>
                </div>
                <p className="text-base">{message.message}</p>
              </div>
            </motion.div>
          ))}
      </AnimatePresence>
    </div>
  );
};

export default StatusMessengerComponent;
