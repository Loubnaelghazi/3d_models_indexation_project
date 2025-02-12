import { ComponentFixture, TestBed } from '@angular/core/testing';

import { IndexationComponent } from './indexation.component';

describe('IndexationComponent', () => {
  let component: IndexationComponent;
  let fixture: ComponentFixture<IndexationComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [IndexationComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(IndexationComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
