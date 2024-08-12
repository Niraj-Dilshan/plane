// helpers
import { API_BASE_URL } from "@/helpers/common.helper";
// plane web types
import { EIssuePropertyType, TIssueProperty, TIssuePropertyOption, TIssuePropertyResponse } from "@/plane-web/types";
// services
import { APIService } from "@/services/api.service";

export class IssuePropertiesService extends APIService {
  constructor() {
    super(API_BASE_URL);
  }

  async fetchAll(workspaceSlug: string, projectId: string): Promise<TIssueProperty<EIssuePropertyType>[]> {
    return this.get(`/api/workspaces/${workspaceSlug}/projects/${projectId}/issue-properties/`)
      .then((response) => response?.data)
      .catch((error) => {
        throw error?.response?.data;
      });
  }

  async create(
    workspaceSlug: string,
    projectId: string,
    issueTypeId: string,
    data: Partial<TIssueProperty<EIssuePropertyType>>,
    options?: Partial<TIssuePropertyOption>[] | undefined
  ): Promise<TIssuePropertyResponse> {
    return this.post(
      `/api/workspaces/${workspaceSlug}/projects/${projectId}/issue-types/${issueTypeId}/issue-properties/`,
      {
        ...data,
        options: options ?? [],
      }
    )
      .then((response) => response?.data)
      .catch((error) => {
        throw error?.response?.data;
      });
  }

  async update(
    workspaceSlug: string,
    projectId: string,
    issueTypeId: string,
    issuePropertyId: string,
    data: Partial<TIssueProperty<EIssuePropertyType>>
  ): Promise<TIssueProperty<EIssuePropertyType>> {
    return this.patch(
      `/api/workspaces/${workspaceSlug}/projects/${projectId}/issue-types/${issueTypeId}/issue-properties/${issuePropertyId}/`,
      data
    )
      .then((response) => response?.data)
      .catch((error) => {
        throw error?.response?.data;
      });
  }

  async deleteProperty(
    workspaceSlug: string,
    projectId: string,
    issueTypeId: string,
    issuePropertyId: string
  ): Promise<void> {
    return this.delete(
      `/api/workspaces/${workspaceSlug}/projects/${projectId}/issue-types/${issueTypeId}/issue-properties/${issuePropertyId}/`
    )
      .then((response) => response?.data)
      .catch((error) => {
        throw error?.response?.data;
      });
  }
}
