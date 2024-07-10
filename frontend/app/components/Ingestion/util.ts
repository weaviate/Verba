export const closeOnClick = () => {
  const elem = document.activeElement;
  if (elem && elem instanceof HTMLElement) {
    elem.blur();
  }
};
