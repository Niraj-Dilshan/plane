import { useEffect, useRef, useState } from "react";
import { observer } from "mobx-react";
import { useSearchParams } from "next/navigation";
// plane editor
import { EditorReadOnlyRefApi, EditorRefApi } from "@plane/editor";
// plane types
import { TPage } from "@plane/types";
// plane ui
import { setToast, TOAST_TYPE } from "@plane/ui";
// components
import { EditorVersionHistoryOverlay } from "@/components/editor";
import { PageEditorHeaderRoot } from "@/components/pages";
// hooks
import { useAppRouter } from "@/hooks/use-app-router";
import { usePageFallback } from "@/hooks/use-page-fallback";
import { useQueryParams } from "@/hooks/use-query-params";
// plane web components
import { WorkspacePageEditorBody, WorkspacePagesVersionEditor } from "@/plane-web/components/pages";
// plane web hooks
import { useWorkspacePages } from "@/plane-web/hooks/store";
// plane web services
import { WorkspacePageService, WorkspacePageVersionService } from "@/plane-web/services/page";
const workspacePageService = new WorkspacePageService();
const workspacePageVersionService = new WorkspacePageVersionService();
// plane web store
import { IWorkspacePageDetails } from "@/plane-web/store/pages/page";

type TPageRootProps = {
  page: IWorkspacePageDetails;
  workspaceSlug: string;
};

export const WorkspacePageRoot = observer((props: TPageRootProps) => {
  const { workspaceSlug, page } = props;
  // states
  const [editorReady, setEditorReady] = useState(false);
  const [readOnlyEditorReady, setReadOnlyEditorReady] = useState(false);
  const [hasConnectionFailed, setHasConnectionFailed] = useState(false);
  const [sidePeekVisible, setSidePeekVisible] = useState(window.innerWidth >= 768);
  const [isVersionsOverlayOpen, setIsVersionsOverlayOpen] = useState(false);
  // refs
  const editorRef = useRef<EditorRefApi>(null);
  const readOnlyEditorRef = useRef<EditorReadOnlyRefApi>(null);
  // router
  const router = useAppRouter();
  // search params
  const searchParams = useSearchParams();
  // store hooks
  const { createPage } = useWorkspacePages();
  // derived values
  const { access, description_html, name, isContentEditable, updateDescription } = page; // page fallback
  usePageFallback({
    editorRef,
    fetchPageDescription: async () => {
      if (!page.id) return;
      return await workspacePageService.fetchDescriptionBinary(workspaceSlug, page.id);
    },
    hasConnectionFailed,
    updatePageDescription: async (data) => await updateDescription(data),
  });
  // update query params
  const { updateQueryParams } = useQueryParams();

  const handleCreatePage = async (payload: Partial<TPage>) => await createPage(payload);

  const handleDuplicatePage = async () => {
    const formData: Partial<TPage> = {
      name: "Copy of " + name,
      description_html: editorRef.current?.getDocument().html ?? description_html ?? "<p></p>",
      access,
    };

    await handleCreatePage(formData)
      .then((res) => router.push(`/${workspaceSlug}/pages/${res?.id}`))
      .catch(() =>
        setToast({
          type: TOAST_TYPE.ERROR,
          title: "Error!",
          message: "Page could not be duplicated. Please try again later.",
        })
      );
  };

  const version = searchParams.get("version");
  useEffect(() => {
    if (!version) {
      setIsVersionsOverlayOpen(false);
      return;
    }
    setIsVersionsOverlayOpen(true);
  }, [version]);

  const handleCloseVersionsOverlay = () => {
    const updatedRoute = updateQueryParams({
      paramsToRemove: ["version"],
    });
    router.push(updatedRoute);
  };

  const handleRestoreVersion = async (descriptionHTML: string) => {
    editorRef.current?.clearEditor();
    editorRef.current?.setEditorValue(descriptionHTML);
  };
  const currentVersionDescription = isContentEditable
    ? editorRef.current?.getDocument().html
    : readOnlyEditorRef.current?.getDocument().html;

  return (
    <>
      <EditorVersionHistoryOverlay
        activeVersion={version}
        currentVersionDescription={currentVersionDescription ?? null}
        editorComponent={WorkspacePagesVersionEditor}
        fetchAllVersions={async (pageId) => {
          if (!workspaceSlug) return;
          return await workspacePageVersionService.fetchAllVersions(workspaceSlug.toString(), pageId);
        }}
        fetchVersionDetails={async (pageId, versionId) => {
          if (!workspaceSlug) return;
          return await workspacePageVersionService.fetchVersionById(workspaceSlug.toString(), pageId, versionId);
        }}
        handleRestore={handleRestoreVersion}
        isOpen={isVersionsOverlayOpen}
        onClose={handleCloseVersionsOverlay}
        entityId={page.id ?? ""}
        restoreEnabled={isContentEditable}
      />
      <PageEditorHeaderRoot
        editorReady={editorReady}
        editorRef={editorRef}
        handleDuplicatePage={handleDuplicatePage}
        page={page}
        readOnlyEditorReady={readOnlyEditorReady}
        readOnlyEditorRef={readOnlyEditorRef}
        setSidePeekVisible={(state) => setSidePeekVisible(state)}
        sidePeekVisible={sidePeekVisible}
      />
      <WorkspacePageEditorBody
        editorRef={editorRef}
        handleConnectionStatus={(status) => setHasConnectionFailed(status)}
        handleEditorReady={(val) => setEditorReady(val)}
        handleReadOnlyEditorReady={() => setReadOnlyEditorReady(true)}
        page={page}
        readOnlyEditorRef={readOnlyEditorRef}
        sidePeekVisible={sidePeekVisible}
      />
    </>
  );
});
