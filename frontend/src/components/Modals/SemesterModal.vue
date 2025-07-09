<template>
	<Dialog
		v-model="show"
		:options="{
			title: SemesterDetail ? __('Edit Semester') : __('Add Semester'),
			size: 'lg',
			actions: [
				{
					label: SemesterDetail ? __('Edit') : __('Create'),
					variant: 'solid',
					onClick: (close) =>
						SemesterDetail ? editSemester(close) : addSemester(close),
				},
			],
		}"
	>
		<template #body-content>
			<div class="space-y-4 text-base">
				<FormControl label="Title" v-model="Semester.title" :required="true" />
				<Switch
					size="sm"
					:label="__('SCORM Package')"
					:description="__('Enable this only if you want to upload a SCORM package as a Semester.')"
					v-model="Semester.is_scorm_package"
				/>
				<div v-if="Semester.is_scorm_package">
					<FileUploader
						v-if="!Semester.scorm_package"
						:fileTypes="['.zip']"
						:validateFile="validateFile"
						@success="(file) => (Semester.scorm_package = file)"
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
								<span>{{ Semester.scorm_package.file_name }}</span>
								<span class="text-sm text-gray-500 mt-1">
									{{ getFileSize(Semester.scorm_package.file_size) }}
								</span>
							</div>
							<X
								@click="() => (Semester.scorm_package = null)"
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
import { defineModel, onMounted, reactive, watch } from 'vue'
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
	SemesterDetail: {
		type: Object,
		default: null,
	},
})

const Semester = reactive({
	title: '',
	is_scorm_package: 0,
	scorm_package: null,
})

const SemesterResource = createResource({
	url: 'lms.lms.api.upsert_Semester',
	makeParams() {
		return {
			title: Semester.title,
			course: props.course,
			is_scorm_package: Semester.is_scorm_package,
			scorm_package: Semester.scorm_package,
			name: props.SemesterDetail?.name,
		}
	},
})

const SemesterReference = createResource({
	url: 'frappe.client.insert',
	makeParams(values) {
		return {
			doc: {
				doctype: 'Course Semester Child',
				semester: values.name,
				parent: props.course,
				parenttype: 'LMS Course',
				parentfield: 'custom_semesters',
			},
		}
	},
})

const addSemester = async (close) => {
	SemesterResource.submit(
		{},
		{
			validate: validateSemester,
			onSuccess(data) {
				capture('Semester_created')
				SemesterReference.submit(
					{ name: data.name },
					{
						onSuccess() {
							cleanSemester()
							if (!settingsStore.onboardingDetails.data?.is_onboarded) {
								settingsStore.onboardingDetails.reload()
							}
							outline.value.reload()
							showToast(__('Success'), __('Semester added successfully'), 'check')
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

const editSemester = (close) => {
	SemesterResource.submit(
		{},
		{
			validate: validateSemester,
			onSuccess() {
				outline.value.reload()
				showToast(__('Success'), __('Semester updated successfully'), 'check')
				close()
			},
			onError(err) {
				showToast(__('Error'), err.messages?.[0] || err, 'x')
			},
		}
	)
}

const validateSemester = () => {
	if (!Semester.title) {
		return __('Semester Title is required')
	}
	if (Semester.is_scorm_package && !Semester.scorm_package) {
		return __('Please upload a SCORM package')
	}
	return true
}

const cleanSemester = () => {
	Semester.title = ''
	Semester.is_scorm_package = 0
	Semester.scorm_package = null
}

watch(
	() => props.SemesterDetail,
	(newSemester) => {
		if (newSemester) {
			Semester.title = newSemester.title || ''
			Semester.is_scorm_package = newSemester.is_scorm_package || 0
			Semester.scorm_package = newSemester.scorm_package || null
		} else {
			cleanSemester()
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

	capture('SemesterModal_loaded', { course: props.course, SemesterDetail: props.SemesterDetail })
})
</script>
