"use client";

import React from "react";

interface UserModalComponentProps {
  modal_id: string;
  title: string;
  text: string;
  triggerAccept?: null | ((a: any) => void);
  triggerValue?: any | null;
  triggerString?: string | null;
}

const UserModalComponent: React.FC<UserModalComponentProps> = ({
  title,
  modal_id,
  text,
  triggerAccept,
  triggerString,
  triggerValue,
}) => {
  return (
    <dialog id={modal_id} className="modal">
      <div className="modal-box flex flex-col gap-2">
        <h3 className="font-bold text-lg">{title}</h3>
        <p className="whitespace-pre-wrap">{text}</p>
        <div className="modal-action">
          <form method="dialog" className="flex gap-2">
            {triggerAccept && triggerString && (
              <button
                className="btn text-text-alt-verba hover:text-text-verba bg-button-verba border-none hover:bg-primary-verba"
                onClick={() => {
                  triggerAccept(triggerValue);
                }}
              >
                {triggerString}
              </button>
            )}
            <button className="btn text-text-alt-verba hover:text-text-verba bg-button-verba border-none hover:bg-warning-verba">
              Cancel
            </button>
          </form>
        </div>
      </div>
    </dialog>
  );
};

export default UserModalComponent;
