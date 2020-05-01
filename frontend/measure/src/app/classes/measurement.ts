export interface CreateMeasurement {
  connection_1: number;
  connection_2: number;
  connection_3: number;
  connection_4: number;
  current_limit: number;
  steps_per_measurement: number;
  name: string;
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
  error: string;
}
