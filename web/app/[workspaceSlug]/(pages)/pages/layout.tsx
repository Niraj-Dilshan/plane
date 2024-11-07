"use client";

// layouts
import { useParams } from "next/navigation";
import { WorkspaceAuthWrapper } from "@/layouts/auth-layout";
// wrappers
import { AuthenticationWrapper } from "@/lib/wrappers";
// plane web components
import { PagesAppCommandPalette } from "@/plane-web/components/command-palette";
import { WithFeatureFlagHOC } from "@/plane-web/components/feature-flags";
import { WorkspacePagesUpgrade } from "@/plane-web/components/pages";
// local components
import { PagesAppSidebar } from "./sidebar";

export default function WorkspacePagesLayout({ children }: { children: React.ReactNode }) {
  // router
  const { workspaceSlug } = useParams();

  return (
    <AuthenticationWrapper>
      <WorkspaceAuthWrapper>
        <WithFeatureFlagHOC
          workspaceSlug={workspaceSlug?.toString()}
          flag="WORKSPACE_PAGES"
          fallback={<WorkspacePagesUpgrade />}
        >
          <>
            <PagesAppCommandPalette />
            <div className="relative flex h-full w-full overflow-hidden">
              <PagesAppSidebar />
              <main className="relative flex h-full w-full flex-col overflow-hidden bg-custom-background-100">
                {children}
              </main>
            </div>
          </>
        </WithFeatureFlagHOC>
      </WorkspaceAuthWrapper>
    </AuthenticationWrapper>
  );
}