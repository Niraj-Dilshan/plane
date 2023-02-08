import { useEffect, useState } from "react";

import Link from "next/link";
import { useRouter } from "next/router";

import { mutate } from "swr";

// react-hook-form
import { Controller, useForm } from "react-hook-form";
// icons
import {
  CalendarDaysIcon,
  ChartPieIcon,
  LinkIcon,
  PlusIcon,
  TrashIcon,
} from "@heroicons/react/24/outline";
// progress-bar
import { CircularProgressbar } from "react-circular-progressbar";
// services
import modulesService from "services/modules.service";
// hooks
import useToast from "hooks/use-toast";
// components
import {
  ModuleLinkModal,
  SidebarLeadSelect,
  SidebarMembersSelect,
  SidebarStatusSelect,
} from "components/modules";

import "react-circular-progressbar/dist/styles.css";
// ui
import { CustomDatePicker, Loader } from "components/ui";
// helpers
import { timeAgo } from "helpers/date-time.helper";
import { copyTextToClipboard } from "helpers/string.helper";
import { groupBy } from "helpers/array.helper";
// types
import { IIssue, IModule, ModuleIssueResponse } from "types";
// fetch-keys
import { MODULE_DETAILS } from "constants/fetch-keys";
import SidebarProgressStats from "components/core/sidebar/sidebar-progress-stats";

const defaultValues: Partial<IModule> = {
  lead: "",
  members_list: [],
  start_date: null,
  target_date: null,
  status: null,
};

type Props = {
  issues: IIssue[];
  module?: IModule;
  isOpen: boolean;
  moduleIssues: ModuleIssueResponse[] | undefined;
  handleDeleteModule: () => void;
};

export const ModuleDetailsSidebar: React.FC<Props> = ({
  issues,
  module,
  isOpen,
  moduleIssues,
  handleDeleteModule,
}) => {
  const [moduleLinkModal, setModuleLinkModal] = useState(false);

  const router = useRouter();
  const { workspaceSlug, projectId, moduleId } = router.query;

  const { setToastAlert } = useToast();

  const { reset, watch, control } = useForm({
    defaultValues,
  });

  const groupedIssues = {
    backlog: [],
    unstarted: [],
    started: [],
    cancelled: [],
    completed: [],
    ...groupBy(moduleIssues ?? [], "issue_detail.state_detail.group"),
  };

  const submitChanges = (data: Partial<IModule>) => {
    if (!workspaceSlug || !projectId || !moduleId) return;

    mutate<IModule>(
      MODULE_DETAILS(moduleId as string),
      (prevData) => ({
        ...(prevData as IModule),
        ...data,
      }),
      false
    );

    modulesService
      .patchModule(workspaceSlug as string, projectId as string, moduleId as string, data)
      .then((res) => {
        console.log(res);
        mutate(MODULE_DETAILS(moduleId as string));
      })
      .catch((e) => {
        console.log(e);
      });
  };

  useEffect(() => {
    if (module)
      reset({
        ...module,
        members_list: module.members_list ?? module.members_detail?.map((m) => m.id),
      });
  }, [module, reset]);

  return (
    <>
      <ModuleLinkModal
        isOpen={moduleLinkModal}
        handleClose={() => setModuleLinkModal(false)}
        module={module}
      />
      <div
        className={`fixed top-0 ${
          isOpen ? "right-0" : "-right-[24rem]"
        } z-20 h-full w-[24rem] overflow-y-auto border-l bg-gray-50 p-5 duration-300`}
      >
        {module ? (
          <>
            <div className="flex items-center justify-between pb-3">
              <h4 className="text-sm font-medium">{module.name}</h4>
              <div className="flex flex-wrap items-center gap-2">
                <button
                  type="button"
                  className="rounded-md border p-2 shadow-sm duration-300 hover:bg-gray-100 focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
                  onClick={() =>
                    copyTextToClipboard(
                      `https://app.plane.so/${workspaceSlug}/projects/${projectId}/modules/${module.id}`
                    )
                      .then(() => {
                        setToastAlert({
                          type: "success",
                          title: "Module link copied to clipboard",
                        });
                      })
                      .catch(() => {
                        setToastAlert({
                          type: "error",
                          title: "Some error occurred",
                        });
                      })
                  }
                >
                  <LinkIcon className="h-3.5 w-3.5" />
                </button>
                <button
                  type="button"
                  className="rounded-md border border-red-500 p-2 text-red-500 shadow-sm duration-300 hover:bg-red-50 focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
                  onClick={() => handleDeleteModule()}
                >
                  <TrashIcon className="h-3.5 w-3.5" />
                </button>
              </div>
            </div>
            <div className="divide-y-2 divide-gray-100 text-xs">
              <div className="py-1">
                <SidebarLeadSelect
                  control={control}
                  submitChanges={submitChanges}
                  lead={module.lead_detail}
                />
                <SidebarMembersSelect control={control} submitChanges={submitChanges} />
                <div className="flex flex-wrap items-center py-2">
                  <div className="flex items-center gap-x-2 text-sm sm:basis-1/2">
                    <ChartPieIcon className="h-4 w-4 flex-shrink-0" />
                    <p>Progress</p>
                  </div>
                  <div className="flex items-center gap-2 sm:basis-1/2">
                    <div className="grid flex-shrink-0 place-items-center">
                      <span className="h-4 w-4">
                        <CircularProgressbar
                          value={groupedIssues.completed.length}
                          maxValue={moduleIssues?.length}
                          strokeWidth={10}
                        />
                      </span>
                    </div>
                    {groupedIssues.completed.length}/{moduleIssues?.length}
                  </div>
                </div>
              </div>
              <div className="py-1">
                <div className="flex flex-wrap items-center py-2">
                  <div className="flex items-center gap-x-2 text-sm sm:basis-1/2">
                    <CalendarDaysIcon className="h-4 w-4 flex-shrink-0" />
                    <p>Start date</p>
                  </div>
                  <div className="sm:basis-1/2">
                    <Controller
                      control={control}
                      name="start_date"
                      render={({ field: { value } }) => (
                        <CustomDatePicker
                          value={value}
                          onChange={(val) =>
                            submitChanges({
                              start_date: val,
                            })
                          }
                        />
                      )}
                    />
                  </div>
                </div>
                <div className="flex flex-wrap items-center py-2">
                  <div className="flex items-center gap-x-2 text-sm sm:basis-1/2">
                    <CalendarDaysIcon className="h-4 w-4 flex-shrink-0" />
                    <p>End date</p>
                  </div>
                  <div className="sm:basis-1/2">
                    <Controller
                      control={control}
                      name="target_date"
                      render={({ field: { value } }) => (
                        <CustomDatePicker
                          value={value}
                          onChange={(val) =>
                            submitChanges({
                              target_date: val,
                            })
                          }
                        />
                      )}
                    />
                  </div>
                </div>
              </div>
              <div className="py-1">
                <SidebarStatusSelect
                  control={control}
                  submitChanges={submitChanges}
                  watch={watch}
                />
              </div>
              <div className="py-1">
                <div className="flex items-center justify-between gap-2">
                  <h4>Links</h4>
                  <button
                    type="button"
                    className="grid h-7 w-7 place-items-center rounded p-1 outline-none duration-300 hover:bg-gray-100"
                    onClick={() => setModuleLinkModal(true)}
                  >
                    <PlusIcon className="h-4 w-4" />
                  </button>
                </div>
                <div className="mt-2 space-y-2">
                  {module.link_module && module.link_module.length > 0
                    ? module.link_module.map((link) => (
                        <div key={link.id} className="group relative">
                          <div className="absolute top-1.5 right-1.5 z-10 opacity-0 group-hover:opacity-100">
                            <button
                              type="button"
                              className="grid h-7 w-7 place-items-center rounded bg-gray-100 p-1 text-red-500 outline-none duration-300 hover:bg-red-50"
                              onClick={() => {
                                const updatedLinks = module.link_module.filter(
                                  (l) => l.id !== link.id
                                );
                                submitChanges({ links_list: updatedLinks });
                              }}
                            >
                              <TrashIcon className="h-4 w-4" />
                            </button>
                          </div>
                          <Link href={link.url} target="_blank">
                            <a className="group relative flex gap-2 rounded-md border bg-gray-100 p-2">
                              <div className="mt-0.5">
                                <LinkIcon className="h-3.5 w-3.5" />
                              </div>
                              <div>
                                <h5>{link.title}</h5>
                                <p className="mt-0.5 text-gray-500">
                                  Added {timeAgo(link.created_at)} ago by{" "}
                                  {link.created_by_detail.email}
                                </p>
                              </div>
                            </a>
                          </Link>
                        </div>
                      ))
                    : null}
                </div>
              </div>
            </div>
            <div className="w-full">
              <SidebarProgressStats issues={issues} groupedIssues={groupedIssues} />
            </div>
          </>
        ) : (
          <Loader>
            <div className="space-y-2">
              <Loader.Item height="15px" width="50%" />
              <Loader.Item height="15px" width="30%" />
            </div>
            <div className="mt-8 space-y-3">
              <Loader.Item height="30px" />
              <Loader.Item height="30px" />
              <Loader.Item height="30px" />
            </div>
          </Loader>
        )}
      </div>
    </>
  );
};
