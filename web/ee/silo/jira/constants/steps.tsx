"use client";
import { Layers2, Layers3, UsersRound, SignalHigh, ReceiptText } from "lucide-react";
// components
import {
  SelectPlaneProjectRoot,
  ConfigureJiraRoot,
  ImportUsersFromJira,
  MapStatesRoot,
  MapPriorityRoot,
  SummaryRoot,
} from "@/plane-web/silo/jira/components";
// types
import { E_IMPORTER_STEPS, TImporterStep } from "@/plane-web/silo/jira/types";

export const IMPORTER_STEPS: TImporterStep[] = [
  {
    key: E_IMPORTER_STEPS.SELECT_PLANE_PROJECT,
    icon: () => <Layers3 size={14} />,
    title: "Configure Plane",
    description:
      "Please first create the project in Plane where you intend to migrate your Jira data. Once the project is created, select it here.",
    component: () => <SelectPlaneProjectRoot />,
    prevStep: undefined,
    nextStep: E_IMPORTER_STEPS.CONFIGURE_JIRA,
  },
  {
    key: E_IMPORTER_STEPS.CONFIGURE_JIRA,
    icon: () => <Layers2 size={14} />,
    title: "Configure Jira",
    description: "Please select the Jira workspace and project from which you want to migrate your data.",
    component: () => <ConfigureJiraRoot />,
    prevStep: E_IMPORTER_STEPS.SELECT_PLANE_PROJECT,
    nextStep: E_IMPORTER_STEPS.IMPORT_USERS_FROM_JIRA,
  },
  {
    key: E_IMPORTER_STEPS.IMPORT_USERS_FROM_JIRA,
    icon: () => <UsersRound size={14} />,
    title: "Import users",
    description:
      "Please add the users you wish to migrate from Jira to Plane. Alternatively, you can skip this step and manually add users later",
    component: () => <ImportUsersFromJira />,
    prevStep: E_IMPORTER_STEPS.CONFIGURE_JIRA,
    nextStep: E_IMPORTER_STEPS.MAP_STATES,
  },
  {
    key: E_IMPORTER_STEPS.MAP_STATES,
    icon: () => <Layers3 size={14} />,
    title: "Map states",
    description:
      "We have automatically matched the Jira statuses to Plane states to the best of our ability. Please map any remaining states before proceeding, you can also create states and map them manually.",
    component: () => <MapStatesRoot />,
    prevStep: E_IMPORTER_STEPS.IMPORT_USERS_FROM_JIRA,
    nextStep: E_IMPORTER_STEPS.MAP_PRIORITY,
  },
  {
    key: E_IMPORTER_STEPS.MAP_PRIORITY,
    icon: () => <SignalHigh size={14} />,
    title: "Map priorities",
    description:
      "We have automatically matched the priorities to the best of our ability. Please map any remaining priorities before proceeding.",
    component: () => <MapPriorityRoot />,
    prevStep: E_IMPORTER_STEPS.MAP_STATES,
    nextStep: E_IMPORTER_STEPS.SUMMARY,
  },
  {
    key: E_IMPORTER_STEPS.SUMMARY,
    icon: () => <ReceiptText size={14} />,
    title: "Summary",
    description: "Here is a summary of the data that will be migrated from Jira to Plane.",
    component: () => <SummaryRoot />,
    prevStep: E_IMPORTER_STEPS.MAP_PRIORITY,
    nextStep: E_IMPORTER_STEPS.SELECT_PLANE_PROJECT,
  },
];