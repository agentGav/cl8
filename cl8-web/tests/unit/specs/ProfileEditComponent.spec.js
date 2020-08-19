import Vue from 'vue'
import { mount } from '@vue/test-utils'

import ProfileEdit from '@/components/profile/ProfileEdit.vue'
import debugLib from 'debug'
const debug = debugLib('cl8.ProfileEditComponent.spec')

let sampleData = {
  admin: 'true',
  bio: '',
  email: 'someone@domain.com',
  visible: 'yes',
  id: 'recxxxxxxxxxxxxxx',
}


describe('ProfileTagsComponent', () => {
  let wrapper, mockStore

  beforeEach(() => {
    mockStore = {
      getters: {
        profile: sampleData,
      },
      dispatch: jest.fn(),
      commit: jest.fn()
    }

    wrapper = mount(ProfileEdit, {
      mocks: {
        $store: mockStore
      }
    })
  })
  it('renders the component', async () => {
    expect(wrapper.html()).toBeTruthy()
  })
})
