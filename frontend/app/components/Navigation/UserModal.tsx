"use client";

import React from "react";

interface UserModalComponentProps {
  modal_id: string;
  title: string;
  text: string;
  triggerAccept?: (a: any) => void;
  triggerValue?: any;
  triggerString?: string;
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
      <div className="modal-box">
        <h3 className="font-bold text-lg">{title}</h3>
        <p className="whitespace-pre-wrap">{text}</p>
        <div className="modal-action">
          <form method="dialog">
            {triggerAccept && triggerValue && triggerString && (
              <button
                className="btn text-text-verba bg-primary-verba border-none hover:bg-button-hover-verba"
                onClick={() => {
                  triggerAccept(triggerValue);
                }}
              >
                {triggerString}
              </button>
            )}
            <button className="btn text-text-verba bg-warning-verba border-none hover:bg-button-hover-verba ml-2">
              Cancel
            </button>
          </form>
        </div>
      </div>
    </dialog>
  );
};

export default UserModalComponent;
