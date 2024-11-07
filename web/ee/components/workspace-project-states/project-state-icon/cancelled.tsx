"use client";

import { FC } from "react";
// types
import { TSvgIcons } from "./types";

export const CancelledIcon: FC<TSvgIcons> = (props) => {
  const { width, height, className, color, ...rest } = props;

  return (
    <>
      <svg
        width={width}
        height={height}
        className={`${className}`}
        viewBox="0 0 18 18"
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
        {...rest}
      >
        <path
          fill-rule="evenodd"
          clip-rule="evenodd"
          d="M14.0003 1.66699H4.00033C2.71166 1.66699 1.66699 2.71166 1.66699 4.00033V14.0003C1.66699 15.289 2.71166 16.3337 4.00033 16.3337H14.0003C15.289 16.3337 16.3337 15.289 16.3337 14.0003V4.00033C16.3337 2.71166 15.289 1.66699 14.0003 1.66699ZM4.00033 0.666992C2.15938 0.666992 0.666992 2.15938 0.666992 4.00033V14.0003C0.666992 15.8413 2.15938 17.3337 4.00033 17.3337H14.0003C15.8413 17.3337 17.3337 15.8413 17.3337 14.0003V4.00033C17.3337 2.15938 15.8413 0.666992 14.0003 0.666992H4.00033Z"
          fill={color}
        />
        <path
          fill-rule="evenodd"
          clip-rule="evenodd"
          d="M13.0578 4.94332C13.2531 5.13858 13.2531 5.45517 13.0578 5.65043L5.65043 13.0578C5.45517 13.2531 5.13858 13.2531 4.94332 13.0578C4.74806 12.8626 4.74806 12.546 4.94332 12.3507L12.3507 4.94332C12.546 4.74806 12.8626 4.74806 13.0578 4.94332Z"
          fill={color}
        />
        <path
          fill-rule="evenodd"
          clip-rule="evenodd"
          d="M4.94332 4.94332C5.13858 4.74806 5.45517 4.74806 5.65043 4.94332L13.0578 12.3507C13.2531 12.546 13.2531 12.8626 13.0578 13.0578C12.8626 13.2531 12.546 13.2531 12.3507 13.0578L4.94332 5.65043C4.74806 5.45517 4.74806 5.13858 4.94332 4.94332Z"
          fill={color}
        />
      </svg>
    </>
  );
};