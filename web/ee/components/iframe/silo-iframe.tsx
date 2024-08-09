"use client";
import { useRef, useCallback, useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { useTheme } from "next-themes";
import useSWR from "swr";
import { LogoSpinner } from "@/components/common";
import { cn } from "@/helpers/common.helper";
import { ServiceAPITokenService } from "@/plane-web/services/api_token.service";

interface CustomIframeProps {
  srcBase: string;
}

const serviceApiTokenService = new ServiceAPITokenService();

const SiloIframe: React.FC<CustomIframeProps> = ({ srcBase }) => {
  const { workspaceSlug } = useParams();
  const ref = useRef<HTMLIFrameElement>(null);
  const { resolvedTheme } = useTheme();
  const [isLoaded, setIsLoaded] = useState<boolean>(false);

  const { data: serviceApiToken } = useSWR(
    workspaceSlug ? `SERVICE_API_TOKEN_${workspaceSlug}` : null,
    workspaceSlug
      ? async () => {
          const serviceApiToken = await serviceApiTokenService.createServiceApiToken(workspaceSlug?.toString(), {});
          return serviceApiToken.token;
        }
      : null
  );

  const sendMessage = useCallback(() => {
    if (!ref.current || !ref.current.contentWindow) {
      console.log("Ref not ready yet");
      return;
    }
    ref.current.contentWindow.postMessage(
      {
        msg: "iframe-theme",
        theme: resolvedTheme,
      },
      "*"
    );
  }, [resolvedTheme]);

  // handle iframe load
  const handleIframeLoad = () => {
    sendMessage();
    setIsLoaded(true);
  };

  // handle theme change
  useEffect(() => {
    sendMessage();
  }, [resolvedTheme, sendMessage]);

  return (
    <div className="relative h-full w-full">
      <iframe
        ref={ref}
        src={`${srcBase}&token=${serviceApiToken}`}
        className={cn("w-full h-full opacity-0 absolute top-0 left-0", {
          "opacity-100": isLoaded,
        })}
        onLoad={handleIframeLoad}
      />
      <div
        className={cn("flex items-center justify-center h-full w-full absolute top-0 left-0 z-10", {
          hidden: isLoaded,
        })}
      >
        <LogoSpinner />
      </div>
    </div>
  );
};

export default SiloIframe;
