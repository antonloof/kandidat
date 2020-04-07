import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';

import { Observable, throwError } from 'rxjs';
import { catchError } from 'rxjs/operators';

import { CreateMeasurement, Measurement } from './classes/measurement';
import { PaginatedList } from './classes/paginated-list';

@Injectable({
  providedIn: 'root',
})
export class BackendService {
  constructor(private http: HttpClient) {}

  create_measurement(measurement: CreateMeasurement): Observable<Measurement> {
    return this.post_request<Measurement>('/api/measurement', measurement);
  }

  get_measurements(filters: any): Observable<PaginatedList<Measurement>> {
    return this.get_request<PaginatedList<Measurement>>(
      '/api/measurement',
      filters
    );
  }

  update_measurement(id: number, payload: any): Observable<Measurement> {
    return this.patch_request<Measurement>('/api/measurement/' + id, payload);
  }

  private handle_error<T>(observable: Observable<T>): Observable<T> {
    return observable.pipe(
      catchError(err => {
        console.log('Http error happened');
        console.error(err);
        return throwError(err);
      })
    );
  }

  private patch_request<T>(url: string, payload: any): Observable<T> {
    return this.handle_error(this.http.patch<T>(url, payload));
  }

  private post_request<T>(url: string, payload: any): Observable<T> {
    return this.handle_error(this.http.post<T>(url, payload));
  }

  private get_request<T>(url: string, query_params: any): Observable<T> {
    return this.handle_error(
      this.http.get<T>(url, { params: query_params })
    );
  }
}
