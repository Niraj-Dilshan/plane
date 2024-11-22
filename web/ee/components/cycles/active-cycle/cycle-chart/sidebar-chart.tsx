import { observer } from "mobx-react";
import { TProgressChartData } from "@/helpers/cycle.helper";
import useCycleDetails from "../use-cycle-details";
import ActiveCycleChart from "./chart";

type TProps = {
  workspaceSlug: string;
  projectId: string;
};

const chartLegends = [
  {
    color: "#26D950",
    label: "Pending",
  },
  {
    color: "#FF9500",
    label: "In-progress",
  },
  {
    color: "#3372FF",
    label: "Scope",
  },
  {
    color: "#6695FF",
    label: "Ideal done",
  },
];

const SidebarChartPro = observer((props: TProps) => {
  const { workspaceSlug, projectId } = props;
  const { cycle, cycleProgress, plotType } = useCycleDetails({
    workspaceSlug: workspaceSlug.toString(),
    projectId: projectId.toString(),
  });
  if (!cycle) return null;
  return (
    <div>
      <div className="h-40 w-full">
        <ActiveCycleChart
          cycle={cycle}
          data={(cycleProgress as TProgressChartData) || []}
          isFullWidth
          plotType={plotType}
        />
      </div>
      <div className="flex items-center justify-between">
        {chartLegends.map((legend, index) => (
          <div className="flex items-center gap-1" key={index}>
            <span
              className="size-2 rounded-full"
              style={{
                backgroundColor: legend.color,
              }}
            />
            <span className="text-xs text-custom-text-300">{legend.label}</span>
          </div>
        ))}
      </div>
    </div>
  );
});
export default SidebarChartPro;