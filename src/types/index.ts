export interface MediaLink {
  id?: number;
  media_type: string;
  url: string;
}

export interface Story {
  id?: number;
  title: string;
  takeoff: string;
  turbulence: string;
  touchdown: string;
  media_links: MediaLink[];
}