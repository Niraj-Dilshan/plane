import { useState } from "react";
import { observer } from "mobx-react";
// ui
import { SubscribeIcon, Tooltip } from "@plane/ui";
// components
import { BulkSubscribeConfirmationModal } from "@/components/issues";
// hooks
import { useAppRouter } from "@/hooks/store";

type Props = {
  handleClearSelection: () => void;
  selectedIssueIds: string[];
};

export const BulkSubscribeIssues: React.FC<Props> = observer((props) => {
  const { handleClearSelection, selectedIssueIds } = props;
  // states
  const [isBulkSubscribeModalOpen, setIsBulkSubscribeModalOpen] = useState(false);
  // store hooks
  const { projectId, workspaceSlug } = useAppRouter();

  return (
    <>
      {projectId && workspaceSlug && (
        <BulkSubscribeConfirmationModal
          isOpen={isBulkSubscribeModalOpen}
          handleClose={() => setIsBulkSubscribeModalOpen(false)}
          issueIds={selectedIssueIds}
          onSubmit={handleClearSelection}
          projectId={projectId.toString()}
          workspaceSlug={workspaceSlug.toString()}
        />
      )}
      <Tooltip tooltipHeading="Subscribe" tooltipContent="">
        <button
          type="button"
          className="outline-none grid place-items-center"
          onClick={() => setIsBulkSubscribeModalOpen(true)}
        >
          <SubscribeIcon className="size-4" />
        </button>
      </Tooltip>
    </>
  );
});