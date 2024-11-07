import { APIService } from "@/services/api.service";
// types
import {
  ClientOptions,
  ExcludedProps,
  ExIssue,
  ExIssueAttachment,
  Optional,
  Paginated,
} from "@/types/types";

export class IssueService extends APIService {
  constructor(options: ClientOptions) {
    super(options);
  }

  async list(slug: string, projectId: string): Promise<Paginated<ExIssue>> {
    return this.get(`/api/v1/workspaces/${slug}/projects/${projectId}/issues/`)
      .then((response) => response.data)
      .catch((error) => {
        throw error?.response?.data;
      });
  }

  async create(
    slug: string,
    projectId: string,
    payload: Omit<Optional<ExIssue>, ExcludedProps>
  ): Promise<ExIssue> {
    return this.post(
      `/api/v1/workspaces/${slug}/projects/${projectId}/issues/`,
      payload
    )
      .then((response) => response.data)
      .catch((error) => {
        throw error?.response?.data;
      });
  }

  async update(
    slug: string,
    projectId: string,
    issueId: string,
    payload: Omit<Optional<ExIssue>, ExcludedProps>
  ) {
    return this.patch(
      `/api/v1/workspaces/${slug}/projects/${projectId}/issues/${issueId}/`,
      payload
    )
      .then((response) => response.data)
      .catch((error) => {
        throw error?.response?.data;
      });
  }

  async destroy(slug: string, projectId: string, issueId: string) {
    return this.delete(
      `/api/v1/workspaces/${slug}/projects/${projectId}/issues/${issueId}/`
    )
      .then((response) => response.data)
      .catch((error) => {
        throw error?.response?.data;
      });
  }

  async createLink(
    slug: string,
    projectId: string,
    issueId: string,
    title: string,
    url: string
  ) {
    return this.post(
      `/api/v1/workspaces/${slug}/projects/${projectId}/issues/${issueId}/links/`,
      {
        title: title,
        url: url,
      }
    )
      .then((response) => response.data)
      .catch((error) => {
        throw error?.response?.data;
      });
  }

  async uploadIssueAttachment(
    workspaceSlug: string,
    projectId: string,
    issueId: string,
    file: FormData
  ): Promise<ExIssueAttachment> {
    return this.post(
      `/api/v1/workspaces/${workspaceSlug}/projects/${projectId}/issues/${issueId}/issue-attachments/`,
      file
    )
      .then((response) => response?.data)
      .catch((error) => {
        throw error?.response?.data;
      });
  }

  async getIssueWithExternalId(
    workspaceSlug: string,
    projectId: string,
    externalId: string,
    externalSource: string
  ): Promise<ExIssue> {
    return this.get(
      `/api/v1/workspaces/${workspaceSlug}/projects/${projectId}/issues/?external_id=${externalId}&external_source=${externalSource}`
    )
      .then((response) => response?.data)
      .catch((error) => {
        throw error?.response?.data;
      });
  }

  async getIssueAttachments(
    workspaceSlug: string,
    projectId: string,
    issueId: string
  ): Promise<ExIssueAttachment[]> {
    return this.get(
      `/api/v1/workspaces/${workspaceSlug}/projects/${projectId}/issues/${issueId}/issue-attachments/`
    )
      .then((response) => response?.data)
      .catch((error) => {
        throw error?.response?.data;
      });
  }
}