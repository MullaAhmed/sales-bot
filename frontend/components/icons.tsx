export const BotIcon = () => {
  return (
    <svg
      height="16"
      strokeLinejoin="round"
      viewBox="0 0 16 16"
      width="16"
      style={{ color: "currentcolor" }}
    >
      <path
        fillRule="evenodd"
        clipRule="evenodd"
        d="M8.75 2.79933C9.19835 2.53997 9.5 2.05521 9.5 1.5C9.5 0.671573 8.82843 0 8 0C7.17157 0 6.5 0.671573 6.5 1.5C6.5 2.05521 6.80165 2.53997 7.25 2.79933V5H7C4.027 5 1.55904 7.16229 1.08296 10H0V13H1V14.5V16H2.5H13.5H15V14.5V13H16V10H14.917C14.441 7.16229 11.973 5 9 5H8.75V2.79933ZM7 6.5C4.51472 6.5 2.5 8.51472 2.5 11V14.5H13.5V11C13.5 8.51472 11.4853 6.5 9 6.5H7ZM7.25 11.25C7.25 12.2165 6.4665 13 5.5 13C4.5335 13 3.75 12.2165 3.75 11.25C3.75 10.2835 4.5335 9.5 5.5 9.5C6.4665 9.5 7.25 10.2835 7.25 11.25ZM10.5 13C11.4665 13 12.25 12.2165 12.25 11.25C12.25 10.2835 11.4665 9.5 10.5 9.5C9.5335 9.5 8.75 10.2835 8.75 11.25C8.75 12.2165 9.5335 13 10.5 13Z"
        fill="currentColor"
      />
    </svg>
  );
};

export const UserIcon = () => {
  return (
    <svg
      data-testid="geist-icon"
      height="16"
      strokeLinejoin="round"
      viewBox="0 0 16 16"
      width="16"
      style={{ color: "currentcolor" }}
    >
      <path
        fillRule="evenodd"
        clipRule="evenodd"
        d="M7.75 0C5.95507 0 4.5 1.45507 4.5 3.25V3.75C4.5 5.54493 5.95507 7 7.75 7H8.25C10.0449 7 11.5 5.54493 11.5 3.75V3.25C11.5 1.45507 10.0449 0 8.25 0H7.75ZM6 3.25C6 2.2835 6.7835 1.5 7.75 1.5H8.25C9.2165 1.5 10 2.2835 10 3.25V3.75C10 4.7165 9.2165 5.5 8.25 5.5H7.75C6.7835 5.5 6 4.7165 6 3.75V3.25ZM2.5 14.5V13.1709C3.31958 11.5377 4.99308 10.5 6.82945 10.5H9.17055C11.0069 10.5 12.6804 11.5377 13.5 13.1709V14.5H2.5ZM6.82945 9C4.35483 9 2.10604 10.4388 1.06903 12.6857L1 12.8353V13V15.25V16H1.75H14.25H15V15.25V13V12.8353L14.931 12.6857C13.894 10.4388 11.6452 9 9.17055 9H6.82945Z"
        fill="currentColor"
      />
    </svg>
  );
};

export const VercelIcon = ({ size = 17 }: { size?: number }) => {
  return (
    <svg
      height={size}
      strokeLinejoin="round"
      viewBox="0 0 16 16"
      width={size}
      style={{ color: "currentcolor" }}
    >
      <path
        fillRule="evenodd"
        clipRule="evenodd"
        d="M8 1L16 15H0L8 1Z"
        fill="currentColor"
      />
    </svg>
  );
};

export const GitIcon = () => {
  return (
    <svg
      height="16"
      strokeLinejoin="round"
      viewBox="0 0 16 16"
      width="16"
      style={{ color: "currentcolor" }}
    >
      <g clipPath="url(#clip0_872_3147)">
        <path
          fillRule="evenodd"
          clipRule="evenodd"
          d="M8 0C3.58 0 0 3.57879 0 7.99729C0 11.5361 2.29 14.5251 5.47 15.5847C5.87 15.6547 6.02 15.4148 6.02 15.2049C6.02 15.0149 6.01 14.3851 6.01 13.7154C4 14.0852 3.48 13.2255 3.32 12.7757C3.23 12.5458 2.84 11.836 2.5 11.6461C2.22 11.4961 1.82 11.1262 2.49 11.1162C3.12 11.1062 3.57 11.696 3.72 11.936C4.44 13.1455 5.59 12.8057 6.05 12.5957C6.12 12.0759 6.33 11.726 6.56 11.5261C4.78 11.3262 2.92 10.6364 2.92 7.57743C2.92 6.70773 3.23 5.98797 3.74 5.42816C3.66 5.22823 3.38 4.40851 3.82 3.30888C3.82 3.30888 4.49 3.09895 6.02 4.1286C6.66 3.94866 7.34 3.85869 8.02 3.85869C8.7 3.85869 9.38 3.94866 10.02 4.1286C11.55 3.08895 12.22 3.30888 12.22 3.30888C12.66 4.40851 12.38 5.22823 12.3 5.42816C12.81 5.98797 13.12 6.69773 13.12 7.57743C13.12 10.6464 11.25 11.3262 9.47 11.5261C9.76 11.776 10.01 12.2558 10.01 13.0056C10.01 14.0752 10 14.9349 10 15.2049C10 15.4148 10.15 15.6647 10.55 15.5847C12.1381 15.0488 13.5182 14.0284 14.4958 12.6673C15.4735 11.3062 15.9996 9.67293 16 7.99729C16 3.57879 12.42 0 8 0Z"
          fill="currentColor"
        />
      </g>
      <defs>
        <clipPath id="clip0_872_3147">
          <rect width="16" height="16" fill="white" />
        </clipPath>
      </defs>
    </svg>
  );
};

export const LoaderIcon = ({ size = 16 }: { size?: number }) => {
  return (
    <svg
      height={size}
      strokeLinejoin="round"
      viewBox="0 0 16 16"
      width={size}
      style={{ color: "currentcolor" }}
    >
      <g clipPath="url(#clip0_2393_1490)">
        <path d="M8 0V4" stroke="currentColor" strokeWidth="1.5" />
        <path
          opacity="0.5"
          d="M8 16V12"
          stroke="currentColor"
          strokeWidth="1.5"
        />
        <path
          opacity="0.9"
          d="M3.29773 1.52783L5.64887 4.7639"
          stroke="currentColor"
          strokeWidth="1.5"
        />
        <path
          opacity="0.1"
          d="M12.7023 1.52783L10.3511 4.7639"
          stroke="currentColor"
          strokeWidth="1.5"
        />
        <path
          opacity="0.4"
          d="M12.7023 14.472L10.3511 11.236"
          stroke="currentColor"
          strokeWidth="1.5"
        />
        <path
          opacity="0.6"
          d="M3.29773 14.472L5.64887 11.236"
          stroke="currentColor"
          strokeWidth="1.5"
        />
        <path
          opacity="0.2"
          d="M15.6085 5.52783L11.8043 6.7639"
          stroke="currentColor"
          strokeWidth="1.5"
        />
        <path
          opacity="0.7"
          d="M0.391602 10.472L4.19583 9.23598"
          stroke="currentColor"
          strokeWidth="1.5"
        />
        <path
          opacity="0.3"
          d="M15.6085 10.4722L11.8043 9.2361"
          stroke="currentColor"
          strokeWidth="1.5"
        />
        <path
          opacity="0.8"
          d="M0.391602 5.52783L4.19583 6.7639"
          stroke="currentColor"
          strokeWidth="1.5"
        />
      </g>
      <defs>
        <clipPath id="clip0_2393_1490">
          <rect width="16" height="16" fill="white" />
        </clipPath>
      </defs>
    </svg>
  );
};

export const ArrowUpIcon = ({ size = 16 }: { size?: number }) => {
  return (
    <svg
      height={size}
      strokeLinejoin="round"
      viewBox="0 0 16 16"
      width={size}
      style={{ color: "currentcolor" }}
    >
      <path
        fillRule="evenodd"
        clipRule="evenodd"
        d="M8.70711 1.39644C8.31659 1.00592 7.68342 1.00592 7.2929 1.39644L2.21968 6.46966L1.68935 6.99999L2.75001 8.06065L3.28034 7.53032L7.25001 3.56065V14.25V15H8.75001V14.25V3.56065L12.7197 7.53032L13.25 8.06065L14.3107 6.99999L13.7803 6.46966L8.70711 1.39644Z"
        fill="currentColor"
      />
    </svg>
  );
};

export const StopIcon = ({ size = 16 }: { size?: number }) => {
  return (
    <svg
      height={size}
      viewBox="0 0 16 16"
      width={size}
      style={{ color: "currentcolor" }}
    >
      <path
        fillRule="evenodd"
        clipRule="evenodd"
        d="M3 3H13V13H3V3Z"
        fill="currentColor"
      />
    </svg>
  );
};

export const MessageIcon = ({ size = 16 }: { size?: number }) => {
  return (
    <svg
      height={size}
      strokeLinejoin="round"
      viewBox="0 0 16 16"
      width={size}
      style={{ color: "currentcolor" }}
    >
      <path
        fillRule="evenodd"
        clipRule="evenodd"
        d="M2.8914 10.4028L2.98327 10.6318C3.22909 11.2445 3.5 12.1045 3.5 13C3.5 13.3588 3.4564 13.7131 3.38773 14.0495C3.69637 13.9446 4.01409 13.8159 4.32918 13.6584C4.87888 13.3835 5.33961 13.0611 5.70994 12.7521L6.22471 12.3226L6.88809 12.4196C7.24851 12.4724 7.61994 12.5 8 12.5C11.7843 12.5 14.5 9.85569 14.5 7C14.5 4.14431 11.7843 1.5 8 1.5C4.21574 1.5 1.5 4.14431 1.5 7C1.5 8.18175 1.94229 9.29322 2.73103 10.2153L2.8914 10.4028ZM2.8135 15.7653C1.76096 16 1 16 1 16C1 16 1.43322 15.3097 1.72937 14.4367C1.88317 13.9834 2 13.4808 2 13C2 12.3826 1.80733 11.7292 1.59114 11.1903C0.591845 10.0221 0 8.57152 0 7C0 3.13401 3.58172 0 8 0C12.4183 0 16 3.13401 16 7C16 10.866 12.4183 14 8 14C7.54721 14 7.10321 13.9671 6.67094 13.9038C6.22579 14.2753 5.66881 14.6656 5 15C4.23366 15.3832 3.46733 15.6195 2.8135 15.7653Z"
        fill="currentColor"
      />
    </svg>
  );
};

export const SparklesIcon = ({ size = 16 }: { size?: number }) => (
  <svg
    height={size}
    strokeLinejoin="round"
    viewBox="0 0 16 16"
    width={size}
    style={{ color: "currentcolor" }}
  >
    <path
      d="M2.5 0.5V0H3.5V0.5C3.5 1.60457 4.39543 2.5 5.5 2.5H6V3V3.5H5.5C4.39543 3.5 3.5 4.39543 3.5 5.5V6H3H2.5V5.5C2.5 4.39543 1.60457 3.5 0.5 3.5H0V3V2.5H0.5C1.60457 2.5 2.5 1.60457 2.5 0.5Z"
      fill="currentColor"
    />
    <path
      d="M14.5 4.5V5H13.5V4.5C13.5 3.94772 13.0523 3.5 12.5 3.5H12V3V2.5H12.5C13.0523 2.5 13.5 2.05228 13.5 1.5V1H14H14.5V1.5C14.5 2.05228 14.9477 2.5 15.5 2.5H16V3V3.5H15.5C14.9477 3.5 14.5 3.94772 14.5 4.5Z"
      fill="currentColor"
    />
    <path
      d="M8.40706 4.92939L8.5 4H9.5L9.59294 4.92939C9.82973 7.29734 11.7027 9.17027 14.0706 9.40706L15 9.5V10.5L14.0706 10.5929C11.7027 10.8297 9.82973 12.7027 9.59294 15.0706L9.5 16H8.5L8.40706 15.0706C8.17027 12.7027 6.29734 10.8297 3.92939 10.5929L3 10.5V9.5L3.92939 9.40706C6.29734 9.17027 8.17027 7.29734 8.40706 4.92939Z"
      fill="currentColor"
    />
  </svg>
);
