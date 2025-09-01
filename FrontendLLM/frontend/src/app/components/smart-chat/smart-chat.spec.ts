import { ComponentFixture, TestBed } from '@angular/core/testing';

import { SmartChat } from './smart-chat';

describe('SmartChat', () => {
  let component: SmartChat;
  let fixture: ComponentFixture<SmartChat>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [SmartChat]
    })
    .compileComponents();

    fixture = TestBed.createComponent(SmartChat);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
