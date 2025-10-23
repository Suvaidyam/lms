<template>
	<Dialog v-model="show" :options="{
			title: ModuleDetail ? __('Edit Module') : __('Add Module'),
			size: 'lg',
			actions: [
				{
					label: ModuleDetail ? __('Edit') : __('Add Module'),
					variant: 'solid',
					onClick: (close) =>
						ModuleDetail ? editModule(close) : addModuleChild(close),
				},
			],
		}">
		<template #body-content>
			<div class="space-y-4 text-base">
				<FormControl v-if="ModuleDetail" label="Title" v-model="Module.title" :required="true" />
				<Link v-else doctype="Course Module" v-model="Module.title" :filters="{  }"
					label="Add Module" :required="true" />
				<Switch size="sm" :label="__('SCORM Package')"
					:description="__('Enable this only if you want to upload a SCORM package as a Module.')"
					v-model="Module.is_scorm_package" />
				<div v-if="Module.is_scorm_package">
					<FileUploader v-if="!Module.scorm_package" :fileTypes="['.zip']" :validateFile="validateFile"
						@success="(file) => (Module.scorm_package = file)">
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
							<X @click="() => (Module.scorm_package = null)"
								class="bg-gray-200 rounded-md cursor-pointer stroke-1.5 w-5 h-5 p-1 ml-4" />
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
import { defineModel, onMounted, reactive, watch } from 'vue'
import { showToast, getFileSize } from '@/utils/'
import { capture } from '@/telemetry'
import { FileText, X } from 'lucide-vue-next'
import { useSettings } from '@/stores/settings'
import Link from '@/components/Controls/Link.vue'

const show = defineModel()
const outline = defineModel('outline')
const settingsStore = useSettings()

const props = defineProps({
	course: {
		type: String,
		required: true,
	},
	semester: {
		type: String,
		default: '',  // This will be the semester.name
	},
	ModuleDetail: {
		type: Object,
		default: null,
	},
	has_semester: {
		type: Boolean,
		default: false,
	},
})

const Module = reactive({
	title: '',
	is_scorm_package: 0,
	scorm_package: null,
})


console.log("ModuleDetail///////////////////////////////////////////////:", props);

const ModuleResource = createResource({
	url: 'lms.lms.api.upsert_Module',
	makeParams() {
		return {
			title: Module.title,
			semester: props.semester,
			semesterTitle: props.semesterTitle,	
			course: props.course,
			is_scorm_package: Module.is_scorm_package,
			scorm_package: Module.scorm_package,
			name: props.ModuleDetail?.name,
		}
	},
})

const ModuleReferenceforsemester = createResource({
	url: 'frappe.client.insert',
	makeParams(values) {
		return {
			doc: {
				doctype: 'Course Module Child',
				module: values.name,
				parent: props.semester,
				parenttype: 'Course Semester',
				parentfield: 'modules',
			},
			
		}
	},
})
const ModuleReferenceforcourse = createResource({
	url: 'frappe.client.insert',
	makeParams(values) {
		return {
			doc: {
				doctype: 'Course Module Child',
				module: values.name,
				parent: props.course,
				parenttype: 'LMS Course',
				parentfield: 'modules',
			},

		}
	},
})


const addModuleChild = async (close) => {
	if (!Module.title) {
		showToast(__('Error'), __('Please select a Module'), 'x')
		return
	}
	const ModuleReference = props.has_semester ? ModuleReferenceforsemester : ModuleReferenceforcourse
	
	ModuleReference.submit(
		{ name: Module.title }, // 👈 take the value selected from Link
		{
			onSuccess() {
				cleanModule()
				if (!settingsStore.onboardingDetails.data?.is_onboarded) {
					settingsStore.onboardingDetails.reload()
				}
				outline.value.reload()
				showToast(__('Success'), __('Module Child added successfully'), 'check')
				close()
			},
			onError(err) {
				showToast(__('Error'), err.messages?.[0] || err, 'x')
			},
		}
	)
}

const addModule = async (close) => {
	ModuleResource.submit(
		{},
		{
			validate: validateModule,
			onSuccess(data) {
				capture('Module_created')
				ModuleReference.submit(
					{ name: data.name },
					{
						onSuccess() {
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
			validate: validateModule,
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
		return __('Module Title is required')
	}
	if (Module.is_scorm_package && !Module.scorm_package) {
		return __('Please upload a SCORM package')
	}
	return true
}

const cleanModule = () => {
	Module.title = ''
	Module.is_scorm_package = 0
	Module.scorm_package = null
}

watch(
	() => props.ModuleDetail,
	(newModule) => {
		if (newModule) {
			Module.title = newModule.title || ''
			Module.is_scorm_package = newModule.is_scorm_package || 0
			Module.scorm_package = newModule.scorm_package || null
		} else {
			cleanModule()
		}
	},
	{ immediate: true }
)

const validateFile = (file) => {
	let extension = file.name.split('.').pop().toLowerCase()
	if (extension !== 'zip') {
		return __('Only zip files are allowed')
	}
}

onMounted(() => {
	
	capture('ModuleModal_loaded', { course: props.course, ModuleDetail: props.ModuleDetail })	
})
</script>
