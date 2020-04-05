import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';

import { Measurement } from './classes/measurement';

@Injectable({
  providedIn: 'root',
})
export class BackendService {
  constructor(private http: HttpClient) {}

  measure(measurement: Measurement) {
    return this.http.post('/api/measurement', measurement);
  }
}
