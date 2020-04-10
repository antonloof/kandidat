export interface CreateMeasurement {
  connection_1: number;
  connection_2: number;
  connection_3: number;
  connection_4: number;
  current_limit: number;
  name: string;
  description?: string;
}

export interface Measurement extends CreateMeasurement {
  id: number;
  open: boolean;
  created_at: string;
  mobility: number;
  sheet_resistance: number;
  amplitude: number;
  angle_freq: number;
  phase: number;
  offset: number;
}

export class measure {
  constructor(
    public id: number,
    public name: string,
    public current: number,
    public speed: string,
    public connection_1: number,
    public connection_2: number,
    public connection_3: number,
    public connection_4: number,
    public description: string,
  ) {  }
}
