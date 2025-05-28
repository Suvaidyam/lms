<template>
	<Dialog
		v-model="show"
		:options="{
			title: ModuleDetail ? __('Edit Module') : __('Add Module'),
			size: 'lg',
			actions: [
				{
					label: ModuleDetail ? __('Edit') : __('Create'),
					variant: 'solid',
					onClick: (close) =>
						ModuleDetail ? editModule(close) : addModule(close),
				},
			],
		}"
	>
		<template #body-content>
			<div class="space-y-4 text-base">
				<FormControl label="Title" v-model="Module.title" :required="true" />
				<Switch
					size="sm"
					:label="__('SCORM Package')"
					:description="__(
						'Enable this only if you want to upload a SCORM package as a Module.'
					)"
					v-model="Module.is_scorm_package"
				/>
				<div v-if="Module.is_scorm_package">
					<FileUploader
						v-if="!Module.scorm_package"
						:fileTypes="['.zip']"
						:validateFile="validateFile"
						@success="(file) => (Module.scorm_package = file)"
					>
						<template v-slot="{ file, progress, uploading, openFileSelector }">
							<div class="mb-4">
								<Button @click="openFileSelector" :loading="uploading">
									{{ uploading ? `Uploading ${progress}%` : 'Upload a zip file' }}
								</Button>
							</div>
						</template>
					</FileUploader>
					<div v-else>
						<div class="flex items-center">
							<div class="border rounded-md p-2 mr-2">
								<FileText class="h-5 w-5 stroke-1.5 text-gray-700" />
							</div>
							<div class="flex flex-col">
								<span>{{ Module.scorm_package.file_name }}</span>
								<span class="text-sm text-gray-500 mt-1">
									{{ getFileSize(Module.scorm_package.file_size) }}
								</span>
							</div>
							<X
								@click="() => (Module.scorm_package = null)"
								class="bg-gray-200 rounded-md cursor-pointer stroke-1.5 w-5 h-5 p-1 ml-4"
							/>
						</div>
					</div>
				</div>
			</div>
		</template>
	</Dialog>
</template>

<script setup>
import {
	Button,
	createResource,
	Dialog,
	FileUploader,
	FormControl,
	Switch,
} from 'frappe-ui'
import { defineModel, reactive, watch } from 'vue'
import { showToast, getFileSize } from '@/utils/'
import { capture } from '@/telemetry'
import { FileText, X } from 'lucide-vue-next'
import { useSettings } from '@/stores/settings'

const show = defineModel()
const outline = defineModel('outline')
const settingsStore = useSettings()

const props = defineProps({
	course: {
		type: String,
		required: true,
	},
	chapterDetail: {
		type: Object,
	},
})
const Module = reactive({
	title: '',
	is_scorm_package: 0,
	scorm_package: null,
})

const ModuleResource = createResource({
	url: 'lms.lms.api.upsert_module',
	makeParams(values) {
		return {
			module_name: Module.title,
            course: props.course,
			is_scorm_package: Module.is_scorm_package,
			scorm_package: Module.scorm_package,
			name: props.ModuleDetail?.name,
		}
	},
})

const ModuleReference = createResource({
	url: 'frappe.client.insert',
	makeParams(values) {
		return {
			doc: {
				doctype: 'Test Course Module',
				module: values.name,
				parent: props.course,
				parenttype: 'LMS Course',
				parentfield: 'custom_module',
			},
		}
	},
})

const addModule = async (close) => {
	ModuleResource.submit(
		{},
		{
			validate() {
				return validateModule()
			},
			onSuccess: (data) => {
				capture('Module_created')
				ModuleReference.submit(
					{ name: data.name },
					{
						onSuccess(data) {
							cleanModule()
							if (!settingsStore.onboardingDetails.data?.is_onboarded) {
								settingsStore.onboardingDetails.reload()
							}
							outline.value.reload()
							showToast(__('Success'), __('Module added successfully'), 'check')
							close()
						},
						onError(err) {
							showToast(__('Error'), err.messages?.[0] || err, 'x')
						},
					}
				)
			},
			onError(err) {
				showToast(__('Error'), err.messages?.[0] || err, 'x')
			},
		}
	)
}

const editModule = (close) => {
	ModuleResource.submit(
		{},
		{
			validate() {
				if (!Module.title) {
					return 'Title is required'
				}
			},
			onSuccess() {
				outline.value.reload()
				showToast(__('Success'), __('Module updated successfully'), 'check')
				close()
			},
			onError(err) {
				showToast(__('Error'), err.messages?.[0] || err, 'x')
			},
		}
	)
}

const validateModule = () => {
	if (!Module.title) {
		return __('Title is required')
	}
	if (Module.is_scorm_package && !Module.scorm_package) {
		return __('Please upload a SCORM package')
	}
}

const cleanModule = () => {
	Module.title = ''
	Module.is_scorm_package = 0
	Module.scorm_package = null
}

watch(
	() => props.ModuleDetail,
	(newModule) => {
		Module.title = newModule?.title
		Module.is_scorm_package = newModule?.is_scorm_package
		Module.scorm_package = newModule?.scorm_package
	}
)

const validateFile = (file) => {
	let extension = file.name.split('.').pop().toLowerCase()
	if (extension !== 'zip') {
		return __('Only zip files are allowed')
	}
}
</script>
