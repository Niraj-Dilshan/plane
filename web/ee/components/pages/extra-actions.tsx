import { useState } from "react";
import { observer } from "mobx-react";
import { useParams } from "next/navigation";
// ui
import { Button } from "@plane/ui";
// helpers
import { SPACE_BASE_PATH, SPACE_BASE_URL } from "@/helpers/common.helper";
// hooks
import { usePage, useUserPermissions } from "@/hooks/store";
// plane web components
import { PublishPageModal } from "@/plane-web/components/pages";
// plane web constants
import { EUserPermissions, EUserPermissionsLevel } from "@/plane-web/constants/user-permissions";
// plane web hooks
import { usePublishPage, useWorkspaceSubscription } from "@/plane-web/hooks/store";
import { useFlag } from "@/plane-web/hooks/store/use-flag";

export const PageDetailsHeaderExtraActions = observer(() => {
  // states
  const [isPublishModalOpen, setIsPublishModalOpen] = useState(false);
  // params
  const { workspaceSlug, projectId, pageId } = useParams();
  // store hooks
  const { allowPermissions } = useUserPermissions();
  const { anchor, isCurrentUserOwner } = usePage(pageId.toString());
  const { fetchProjectPagePublishSettings, getPagePublishSettings, publishProjectPage, unpublishProjectPage } =
    usePublishPage();
  const { togglePaidPlanModal } = useWorkspaceSubscription();
  const isPagePublishEnabled = useFlag(workspaceSlug?.toString(), "PAGE_PUBLISH");
  // derived values
  const isDeployed = !!anchor;
  const pagePublishSettings = getPagePublishSettings(pageId.toString());

  const isPublishAllowed = allowPermissions(
    [EUserPermissions.ADMIN, EUserPermissions.MEMBER],
    EUserPermissionsLevel.PROJECT
  );

  const SPACE_APP_URL = SPACE_BASE_URL.trim() === "" ? window.location.origin : SPACE_BASE_URL;
  const publishLink = `${SPACE_APP_URL}${SPACE_BASE_PATH}/pages/${anchor}`;

  if (!isPagePublishEnabled)
    return (
      <Button variant="accent-primary" size="sm" onClick={() => togglePaidPlanModal(true)}>
        Upgrade to publish
      </Button>
    );

  return (
    <>
      <PublishPageModal
        anchor={anchor}
        fetchPagePublishSettings={async () =>
          await fetchProjectPagePublishSettings(projectId.toString(), pageId.toString())
        }
        isOpen={isPublishModalOpen}
        onClose={() => setIsPublishModalOpen(false)}
        pagePublishSettings={pagePublishSettings}
        publishPage={(data) => publishProjectPage(projectId.toString(), pageId.toString(), data)}
        unpublishPage={() => unpublishProjectPage(projectId.toString(), pageId.toString())}
      />
      {isDeployed && (
        <a
          href={publishLink}
          className="px-3 py-1.5 bg-green-500/20 text-green-500 rounded text-xs font-medium flex items-center gap-1.5"
          target="_blank"
          rel="noopener noreferrer"
        >
          <span className="flex-shrink-0 rounded-full size-1.5 bg-green-500" />
          Live
        </a>
      )}
      {isCurrentUserOwner && isPublishAllowed && (
        <Button variant="outline-primary" size="sm" onClick={() => setIsPublishModalOpen(true)}>
          {isDeployed ? "Unpublish" : "Publish"}
        </Button>
      )}
    </>
  );
});