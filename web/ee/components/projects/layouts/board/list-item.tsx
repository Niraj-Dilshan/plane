"use client";

import { FC, useEffect, useRef } from "react";
import { combine } from "@atlaskit/pragmatic-drag-and-drop/combine";
import { draggable } from "@atlaskit/pragmatic-drag-and-drop/element/adapter";
import { observer } from "mobx-react";
import { useParams } from "next/navigation";
// hooks
import { setToast, TOAST_TYPE } from "@plane/ui";
import { useProject, useUserPermissions } from "@/hooks/store";
// plane web components
import { ProjectCard } from "@/plane-web/components/projects/layouts/gallery/card";
// plane web constants
import { EUserPermissions } from "@/plane-web/constants/user-permissions";
// plane web types
import { TProject } from "@/plane-web/types/projects";

type ProjectBoardListItem = {
  groupByKey: string;
  projectId: string;
};

export const ProjectBoardListItem: FC<ProjectBoardListItem> = observer((props) => {
  const { projectId } = props;
  // router
  const { workspaceSlug } = useParams();
  // hooks
  const { getProjectById } = useProject();
  const { workspaceProjectsPermissions } = useUserPermissions();

  // derived values
  const project = getProjectById(projectId) as TProject;
  const cardRef = useRef<HTMLDivElement | null>(null);
  const isDragAllowed =
    workspaceProjectsPermissions &&
    workspaceProjectsPermissions[workspaceSlug.toString()][projectId] &&
    workspaceProjectsPermissions[workspaceSlug.toString()][projectId] >= EUserPermissions.ADMIN;
  if (!project) return <></>;

  useEffect(() => {
    const element = cardRef.current;

    if (!element) return;

    return combine(
      draggable({
        element,
        dragHandle: element,
        canDrag: () => isDragAllowed,
        getInitialData: () => ({ id: project.id, type: "PROJECT" }),
      })
    );
  }, [cardRef?.current, project, isDragAllowed]);
  return (
    <div
      className="flex whitespace-nowrap gap-2 rounded w-full"
      ref={cardRef}
      id={`kanban-${project.id}`}
      onDragStart={() => {
        if (!isDragAllowed) {
          setToast({
            title: "Warning!",
            type: TOAST_TYPE.ERROR,
            message: "You don't have permission to move this project",
          });
        }
      }}
    >
      <ProjectCard project={project} />
    </div>
  );
});