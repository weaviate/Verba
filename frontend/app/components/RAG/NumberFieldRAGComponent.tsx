"use client";

import React from "react";

import { NumberFieldSetting } from "../Settings/types";
import { RAGConfig } from "./types";

interface NumberFieldRAGComponentProps {
  title: string;
  NumberFieldSetting: NumberFieldSetting;
  RAGConfig: RAGConfig;
  RAGConfigTitle: string;
  RAGComponentTitle: string;
  setRAGConfig: (r_: any) => void;
}

const NumberFieldRAGComponent: React.FC<NumberFieldRAGComponentProps> = ({
  title,
  NumberFieldSetting,
  RAGConfig,
  RAGConfigTitle,
  RAGComponentTitle,
  setRAGConfig,
}) => {
  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const newText = e.target.value;
    setRAGConfig((prevConfig: any) => {
      const newConfig = JSON.parse(JSON.stringify(prevConfig));
      console.log(newConfig[RAGConfigTitle].components[RAGComponentTitle]);
      newConfig[RAGConfigTitle].components[RAGComponentTitle].config[
        title
      ].value = newText;
      return newConfig;
    });
  };

  return (
    <div key={title} className="flex flex-col gap-1">
      <div className="flex items-center justify-center lg:text-base text-sm">
        <p>{NumberFieldSetting.description}</p>
      </div>
      <div className="flex items-center justify-center">
        <label className="input input-bordered flex items-center gap-2 w-full lg:text-base text-sm bg-bg-verba">
          <input
            type="number"
            className="grow"
            placeholder={title}
            value={
              (
                RAGConfig[RAGConfigTitle].components[RAGComponentTitle]
                  .config as any
              )[title].value
            }
            onChange={handleChange}
          />
        </label>
      </div>
    </div>
  );
};

export default NumberFieldRAGComponent;
