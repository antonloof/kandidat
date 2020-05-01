import { TestBed } from '@angular/core/testing';

import { RandomNameService } from './random-name.service';

describe('RandomNameService', () => {
  let service: RandomNameService;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(RandomNameService);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
