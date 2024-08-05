import { useState } from "react";
import { observer } from "mobx-react";
import { usePopper } from "react-popper";
import { ChevronDown } from "lucide-react";
import { Popover } from "@headlessui/react";
// ui
import { Input, TextArea, Tooltip } from "@plane/ui";
// helpers
import { cn } from "@/helpers/common.helper";
// plane web types
import { EIssuePropertyType, TIssueProperty, TOperationMode } from "@/plane-web/types";

type TPropertyTitleDropdownProps = {
  propertyDetail: Partial<TIssueProperty<EIssuePropertyType>>;
  currentOperationMode: TOperationMode | null;
  error?: string;
  onPropertyDetailChange: <K extends keyof TIssueProperty<EIssuePropertyType>>(
    key: K,
    value: TIssueProperty<EIssuePropertyType>[K],
    shouldSync?: boolean
  ) => void;
};

// TODO: Update to use CustomMenu
export const PropertyTitleDropdown = observer((props: TPropertyTitleDropdownProps) => {
  const { propertyDetail, currentOperationMode, error, onPropertyDetailChange } = props;
  // states
  const [referenceElement, setReferenceElement] = useState<HTMLButtonElement | null>(null);
  const [popperElement, setPopperElement] = useState<HTMLDivElement | null>(null);

  const { styles, attributes } = usePopper(referenceElement, popperElement, {
    placement: "bottom-start",
  });

  if (!currentOperationMode) {
    return (
      <Tooltip tooltipContent={propertyDetail.description} position="top-left" disabled={!propertyDetail.description}>
        <span className="px-1 truncate">{propertyDetail.display_name ?? ""}</span>
      </Tooltip>
    );
  }

  return (
    <Popover>
      <Popover.Button as="div">
        <button
          type="button"
          className={cn(
            "w-full flex items-center justify-between px-2 py-1 text-sm gap-1 bg-custom-background-100 hover:bg-custom-background-80 border-[0.5px] border-custom-border-300 rounded cursor-pointer outline-none",
            Boolean(error) && "border-red-500",
            !propertyDetail.display_name && "py-2"
          )}
          ref={setReferenceElement}
        >
          <span className="text-custom-text-200">{propertyDetail.display_name ?? ""}</span>
          <ChevronDown className="h-3 w-3" aria-hidden="true" />
        </button>
      </Popover.Button>
      <Popover.Panel className="fixed z-10">
        <div
          className="w-72 flex flex-col bg-custom-background-100 border-[0.5px] border-custom-border-300 rounded my-1 p-2 gap-2 shadow-custom-shadow-rg"
          ref={setPopperElement}
          style={styles.popper}
          {...attributes.popper}
        >
          <div>
            <div className="text-xs font-medium text-custom-text-300">Name</div>
            <Input
              id="display_name"
              type="text"
              value={propertyDetail.display_name}
              onChange={(e) => onPropertyDetailChange("display_name", e.target.value)}
              className={cn("w-full resize-none text-sm px-1.5 py-0.5 bg-custom-background-100 border-[0.5px] rounded")}
              tabIndex={1}
              hasError={Boolean(error)}
              placeholder={error}
              required
              autoFocus
            />
          </div>
          <div>
            <div className="text-xs font-medium text-custom-text-300">Description (optional)</div>
            <TextArea
              id="description"
              value={propertyDetail.description}
              onChange={(e) => onPropertyDetailChange("description", e.target.value)}
              className={cn("w-full resize-none text-sm px-1.5 py-0.5 bg-custom-background-100 border-[0.5px] rounded")}
              tabIndex={2}
            />
          </div>
        </div>
      </Popover.Panel>
    </Popover>
  );
});
